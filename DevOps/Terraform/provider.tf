provider "google" {
  credentials = file("terraform-key.json")
  project     = "graphite-byte-472516-n8"
  region      = "us-central1"
}

terraform {  
  backend "gcs" {
     credentials = "terraform-key.json"
    bucket = "terraform-sauter-university"  
  }
}
