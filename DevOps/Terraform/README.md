
Terraform

Objetivo: criar e gerenciar a infraestrutura do projeto na nuvem (GCP) usando IaC.

Arquivos principais:
main.tf → recursos principais
variables.tf → variáveis do projeto
outputs.tf → saídas usadas em outras partes do projeto
provider.tf → configura o provedor GCP
.terraform.lock.hcl → bloqueio de versões do Terraform

Como usar:
terraform init     # inicializa o projeto
terraform plan     # mostra o que será criado/alterado (sempre conferir)
terraform apply    # aplica as mudanças
