import logging
import re
import requests
import pandas as pd
import numpy as np
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

BASE_URL = "https://dados.ons.org.br/api/3/action/package_show?id="
app = FastAPI()

# --------- helpers for robust numeric/date sanitization ----------
SAFE_FLOAT_ABS_MAX = 1e15
_scientific_re = re.compile(r'^[\+\-]?\d+([.,]\d+)?[eE][\+\-]?\d+$')

def _looks_like_number_string(s: Any) -> bool:
    if s is None:
        return False
    ss = str(s).strip()
    if ss == "":
        return False
    # if contains letters aside from E/e, probably not numeric
    if re.search(r'[A-DF-Za-df-z]', ss.replace(",", "").replace(".", "")):
        return False
    return bool(re.search(r'\d', ss))

def safe_parse_number(s: Any) -> Optional[float]:
    if s is None:
        return None
    if isinstance(s, (int, np.integer)):
        return int(s)
    if isinstance(s, (float, np.floating)):
        if np.isfinite(s) and abs(float(s)) <= SAFE_FLOAT_ABS_MAX:
            return float(s)
        return None
    s_str = str(s).strip()
    if s_str == "":
        return None
    # scientific with comma -> replace comma
    try:
        if _scientific_re.match(s_str.replace(",", ".")):
            val = float(s_str.replace(",", "."))
            return float(val) if (np.isfinite(val) and abs(val) <= SAFE_FLOAT_ABS_MAX) else None
    except:
        pass
    # direct parse (comma decimal -> dot)
    try:
        val = float(s_str.replace(",", "."))
        return float(val) if (np.isfinite(val) and abs(val) <= SAFE_FLOAT_ABS_MAX) else None
    except:
        pass
    # remove thousand separators (dots) then comma->dot
    try:
        candidate = s_str.replace(".", "").replace(",", ".")
        val = float(candidate)
        return float(val) if (np.isfinite(val) and abs(val) <= SAFE_FLOAT_ABS_MAX) else None
    except:
        return None

def sanitize_numeric_columns_in_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    For object columns that 'look like' numeric, parse them safely.
    Also sanitize existing numeric dtypes to clip inf/NaN/too large -> None.
    """
    # object columns: if sample looks numeric, parse
    for col in df.columns:
        if df[col].dtype == "object" and col != "ear_data":
            sample = df[col].dropna().astype(str).head(50)
            if any(_looks_like_number_string(x) for x in sample):
                df[col] = df[col].apply(lambda x: safe_parse_number(x))
    # numeric dtype columns: sanitize values
    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].apply(lambda x: float(x) if (x is not None and np.isfinite(x) and abs(float(x)) <= SAFE_FLOAT_ABS_MAX) else None)
    return df

def sanitize_records_for_json(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sanitized: List[Dict[str, Any]] = []
    for row in records:
        new_row: Dict[str, Any] = {}
        for k, v in row.items():
            # numpy ints
            if isinstance(v, (np.integer,)):
                new_row[k] = int(v)
                continue
            # numpy floats
            if isinstance(v, (np.floating,)):
                fv = float(v)
                new_row[k] = fv if (np.isfinite(fv) and abs(fv) <= SAFE_FLOAT_ABS_MAX) else None
                continue
            # pandas Timestamp or datetime-like -> ISO date
            try:
                # pandas Timestamp has .strftime
                if hasattr(v, "strftime"):
                    new_row[k] = v.strftime("%Y-%m-%d")
                    continue
            except Exception:
                pass
            # python float
            if isinstance(v, float):
                new_row[k] = v if (np.isfinite(v) and abs(v) <= SAFE_FLOAT_ABS_MAX) else None
                continue
            # strings: strip and convert empty -> None
            if isinstance(v, str):
                s = v.strip()
                new_row[k] = s if s != "" else None
                continue
            # None, ints, bools, etc: keep as-is
            new_row[k] = v
        sanitized.append(new_row)
    return sanitized

# --------- ONS metadata helpers ----------

def fetch_package_metadata(package_id: str) -> dict:
    url = f"{BASE_URL}{package_id}"
    logging.info(f"Fetching resources for package_id={package_id}")
    resp = requests.get(url, timeout=(5, 30))
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success"):
        raise ValueError("Resposta inválida da API do ONS")
    return data["result"]

def find_csv_url(metadata: dict, ano: int) -> str:
    resources = metadata.get("resources", [])
    csvs = [r for r in resources if r.get("format", "").upper() == "CSV"]
    logging.info(f"{len(csvs)} CSV resources found.")
    for r in csvs:
        if str(ano) in r.get("name", "") or str(ano) in r.get("url", ""):
            logging.info(f"Using CSV: {r['url']}")
            return r["url"]
    raise ValueError(f"No CSV found for ano {ano}.")

# --------- pagination endpoint core: read by chunks ----------

def page_csv_via_chunks(
    csv_url: str,
    page: int = 1,
    page_size: int = 100,
    ano: Optional[int] = None,
    mes: Optional[int] = None,
    nome_reservatorio: Optional[str] = None,
    chunksize: int = 20000
) -> Dict[str, Any]:
    """
    Reads CSV in chunks, filters per chunk, and returns up to page_size rows for the requested page.
    Returns a dict {page, page_size, has_more, data}.
    This does not compute total count (would require full scan).
    """
    assert page >= 1 and page_size >= 1
    start_idx = (page - 1) * page_size
    need = page_size + 1  # read one extra to detect if there's more
    collected: List[Dict[str, Any]] = []
    matched_count = 0  # how many matching rows we have seen (filtered)

    logging.info(f"Paginating CSV {csv_url} page={page} page_size={page_size} chunksize={chunksize}")

    # read in chunks; pandas can read directly from URL
    try:
        reader = pd.read_csv(csv_url, sep=";", encoding="utf-8", na_values=["######", "", " "], low_memory=True, chunksize=chunksize)
    except Exception as e:
        # if encoding utf-8 fails (rare), try latin-1
        logging.warning(f"read_csv with utf-8 failed: {e}; trying latin-1")
        reader = pd.read_csv(csv_url, sep=";", encoding="latin-1", na_values=["######", "", " "], low_memory=True, chunksize=chunksize)

    for chunk in reader:
        # normalize ear_data early (if present)
        if "ear_data" in chunk.columns:
            chunk["ear_data"] = pd.to_datetime(chunk["ear_data"].astype(str).str.strip(), errors="coerce", dayfirst=True)

        # apply year/month filters (faster to drop non-matching rows early)
        if ano and "ear_data" in chunk.columns:
            chunk = chunk[chunk["ear_data"].dt.year == ano]
        if mes and "ear_data" in chunk.columns:
            chunk = chunk[chunk["ear_data"].dt.month == mes]

        # filter by nome_reservatorio if present
        if nome_reservatorio and "nom_reservatorio" in chunk.columns:
            chunk = chunk[chunk["nom_reservatorio"].astype(str).str.contains(nome_reservatorio, case=False, na=False)]

        if chunk.empty:
            continue

        # sanitize numeric-like columns and numeric dtypes in this chunk
        chunk = sanitize_numeric_columns_in_df(chunk)

        # convert datetime columns to string for JSON
        for c in chunk.select_dtypes(include=["datetime64[ns]"]):
            chunk[c] = chunk[c].apply(lambda x: x.strftime("%Y-%m-%d") if pd.notnull(x) else None)

        # iterate rows (ordered) and collect only the ones for requested page
        for _, row in chunk.iterrows():
            # row is a Series; convert to dict
            if matched_count < start_idx:
                matched_count += 1
                continue
            if len(collected) < need:
                collected.append(row.to_dict())
            else:
                break

        if len(collected) >= need:
            # we have enough to decide has_more -> break out
            break

    # determine has_more and trim to page_size
    has_more = len(collected) > page_size
    if has_more:
        data = collected[:page_size]
    else:
        data = collected

    # final sanitization pass on collected rows (convert numpy types, remove inf/nan)
    data = sanitize_records_for_json(data)

    return {
        "page": page,
        "page_size": page_size,
        "has_more": has_more,
        "data": data
    }

# --------- FastAPI endpoint (pagination) ----------

@app.get("/data")
def get_data(
    package_id: str = Query(..., description="ID do pacote ONS"),
    ano: int = Query(..., description="Ano desejado"),
    mes: int = Query(None, description="Mês desejado (opcional)"),
    nome_reservatorio: str = Query(None, description="Filtrar por nome do reservatório"),
    page: int = Query(1, description="Página (1-based)"),
    page_size: int = Query(100, description="Número de itens por página (max advisable ~1000)")
):
    logging.info(f"New request: package_id={package_id}, ano={ano}, mes={mes}, nome_reservatorio={nome_reservatorio}, page={page}, page_size={page_size}")
    try:
        metadata = fetch_package_metadata(package_id)
        csv_url = find_csv_url(metadata, ano)
        result = page_csv_via_chunks(csv_url, page=page, page_size=page_size, ano=ano, mes=mes, nome_reservatorio=nome_reservatorio)
        return JSONResponse(content=result)
    except Exception as e:
        logging.error(f"Error processing request: {e}", exc_info=True)
        return JSONResponse(content={"error": str(e)}, status_code=500)
