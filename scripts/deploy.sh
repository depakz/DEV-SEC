#!/usr/bin/env bash
# One-time setup of the Azure Storage account that holds Terraform's
# remote state (the `backend "azurerm" {}` block in terraform/providers.tf).
# Run this once, by hand, before the first `terraform init`. Jenkins never
# calls this script — the Jenkinsfile's "Deploy via Terraform" stage runs
# `terraform apply` directly against the state this script creates.
set -euo pipefail

RESOURCE_GROUP="tfstate-rg"
LOCATION="${1:-eastus}"
STORAGE_ACCOUNT="tfstate$(date +%s | tail -c 6)" # must be globally unique
CONTAINER_NAME="tfstate"

echo "Creating Terraform remote-state storage in $LOCATION ..."

az group create --name "$RESOURCE_GROUP" --location "$LOCATION"

az storage account create \
    --name "$STORAGE_ACCOUNT" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --sku Standard_LRS \
    --encryption-services blob

az storage container create \
    --name "$CONTAINER_NAME" \
    --account-name "$STORAGE_ACCOUNT"

cat <<EOF

Done. Add this to terraform/providers.tf's backend "azurerm" block,
then run: terraform init -migrate-state

  resource_group_name  = "$RESOURCE_GROUP"
  storage_account_name = "$STORAGE_ACCOUNT"
  container_name       = "$CONTAINER_NAME"
  key                  = "security-scanner.tfstate"
EOF
