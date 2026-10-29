terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.95"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  # Remote state in Azure Storage, so `terraform.tfstate` is never a local
  # file sitting next to the code (and so Jenkins can plan/apply against
  # the same state this machine does). Create the storage account once,
  # by hand or with scripts/bootstrap-state.sh, then uncomment this block
  # and run `terraform init -migrate-state`.
  #
  # backend "azurerm" {
  #   resource_group_name  = "tfstate-rg"
  #   storage_account_name = "tfstateacctXXXX"   # must be globally unique
  #   container_name       = "tfstate"
  #   key                  = "security-scanner.tfstate"
  # }
}

provider "azurerm" {
  features {}
  # Auth comes from `az login` (local) or ARM_* environment variables (CI/Jenkins):
  # ARM_CLIENT_ID, ARM_CLIENT_SECRET, ARM_SUBSCRIPTION_ID, ARM_TENANT_ID
}
