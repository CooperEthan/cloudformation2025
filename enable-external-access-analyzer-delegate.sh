#!/bin/bash

# === Script to configure AWS Access Analyzer for Organization ===
# 1. Registers a delegated administrator account for Access Analyzer (run in management account)
# 2. Creates an organization-level analyzer in management account (type = ORGANIZATION)
# 
# Usage: ./enable-org-access-analyzer.sh <delegated-account-id> <mgmt-profile>
# Example: ./enable-org-access-analyzer.sh 123456789012 mgmt-profile

# === Validate Input ===
if [ $# -ne 2 ]; then
  echo "Usage: $0 <delegated-account-id> <mgmt-profile>"
  echo "Example: $0 123456789012 mgmt-profile"
  exit 1
fi

DELEGATED_ACCOUNT_ID=$1
MGMT_PROFILE=$2
REGION="us-east-1"  # Region where org analyzer will be created
ANALYZER_NAME="org-analyzer"

echo "==> Using delegated account ID: $DELEGATED_ACCOUNT_ID"
echo "==> Using management account profile: $MGMT_PROFILE"
echo "==> Region: $REGION"
echo "==> Analyzer name: $ANALYZER_NAME"
echo

# === Step 1: Register delegated administrator ===
echo "==> Registering delegated administrator account ($DELEGATED_ACCOUNT_ID)..."

aws organizations register-delegated-administrator \
  --account-id $DELEGATED_ACCOUNT_ID \
  --service-principal access-analyzer.amazonaws.com \
  --profile $MGMT_PROFILE

if [ $? -eq 0 ]; then
  echo "Delegated administrator registered successfully."
else
  echo "Failed to register delegated administrator."
  exit 1
fi

echo

# === Step 2: Create organization-level analyzer ===
echo "==> Creating organization-level Access Analyzer ($ANALYZER_NAME)..."

aws accessanalyzer create-analyzer \
  --analyzer-name $ANALYZER_NAME \
  --type ORGANIZATION \
  --region $REGION \
  --profile $MGMT_PROFILE

if [ $? -eq 0 ]; then
  echo "✅ Organization-level Access Analyzer created successfully."
else
  echo "Failed to create organization-level analyzer (it might already exist)."
fi