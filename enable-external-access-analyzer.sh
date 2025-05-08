#!/bin/bash

# ----- CONFIGURATION -----
ANALYZER_NAME="org-analyzer"
ANALYZER_TYPE="ORGANIZATION"
ARCHIVE_RULE_NAME="exclude-org-accounts"
# Example archive rule filter — adjust as needed
ARCHIVE_RULE_FILTER='{"isPublic": {"eq": ["false"]}, "principal.IsAWSOrganizationMember": {"eq": ["true"]}}'
# -------------------------

# Get all enabled AWS regions
regions=$(aws ec2 describe-regions --all-regions --query "Regions[?OptInStatus=='opt-in-not-required'||OptInStatus=='opted-in'].RegionName" --output text)

echo "Regions found: $regions"
echo "Creating analyzer '$ANALYZER_NAME' in all regions..."

for region in $regions; do
  echo "Processing region: $region"

  # Check if analyzer already exists
  exists=$(aws accessanalyzer list-analyzers --region $region --query "analyzers[?name=='$ANALYZER_NAME'] | length(@)" --output text)

  if [ "$exists" -eq 0 ]; then
    echo "  Creating analyzer in $region..."
    aws accessanalyzer create-analyzer \
      --analyzer-name $ANALYZER_NAME \
      --type $ANALYZER_TYPE \
      --region $region
  else
    echo "  Analyzer already exists in $region. Skipping creation."
  fi

  # Check if archive rule already exists
  rule_exists=$(aws accessanalyzer list-archive-rules --analyzer-name $ANALYZER_NAME --region $region --query "archiveRules[?ruleName=='$ARCHIVE_RULE_NAME'] | length(@)" --output text)

  if [ "$rule_exists" -eq 0 ]; then
    echo "  Creating archive rule in $region..."
    aws accessanalyzer create-archive-rule \
      --analyzer-name $ANALYZER_NAME \
      --rule-name $ARCHIVE_RULE_NAME \
      --filter "$ARCHIVE_RULE_FILTER" \
      --region $region
  else
    echo "  Archive rule already exists in $region. Skipping."
  fi

done

echo "✅ Automation complete."
