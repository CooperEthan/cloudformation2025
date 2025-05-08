#!/bin/bash

# Set your profile and region
PROFILE=prod
REGION=us-east-1
ACCOUNT_ID=599326816772  # <-- replace with YOUR management account ID

### 1️⃣ Delete S3 Buckets (Audit + Logging buckets — replace suffix if you used custom names)

aws s3 rb s3://aws-controltower-audit-logs-${ACCOUNT_ID}-${REGION} --force --profile $PROFILE
aws s3 rb s3://aws-controltower-s3-access-logs-${ACCOUNT_ID}-${REGION} --force --profile $PROFILE

# If you created custom buckets with a suffix:
# aws s3 rb s3://aws-controltower-audit-logs-${ACCOUNT_ID}-${REGION}-unique789 --force --profile $PROFILE
# aws s3 rb s3://aws-controltower-s3-access-logs-${ACCOUNT_ID}-${REGION}-unique789 --force --profile $PROFILE

### 2️⃣ Delete CloudTrails

TRAILS=$(aws cloudtrail list-trails --profile $PROFILE --region $REGION --query 'trailList[].Name' --output text)
for trail in $TRAILS; do
  echo "Deleting CloudTrail $trail"
  aws cloudtrail delete-trail --name $trail --profile $PROFILE --region $REGION
done

### 3️⃣ Delete AWS Config recorders & rules

# Stop Config recorders
RECORDERS=$(aws configservice describe-configuration-recorders --profile $PROFILE --region $REGION --query 'ConfigurationRecorders[].name' --output text)
for recorder in $RECORDERS; do
  echo "Stopping Config recorder $recorder"
  aws configservice stop-configuration-recorder --configuration-recorder-name $recorder --profile $PROFILE --region $REGION
done

# Delete Config recorders
for recorder in $RECORDERS; do
  echo "Deleting Config recorder $recorder"
  aws configservice delete-configuration-recorder --configuration-recorder-name $recorder --profile $PROFILE --region $REGION
done

# Delete Config rules
RULES=$(aws configservice describe-config-rules --profile $PROFILE --region $REGION --query 'ConfigRules[].ConfigRuleName' --output text)
for rule in $RULES; do
  echo "Deleting Config rule $rule"
  aws configservice delete-config-rule --config-rule-name $rule --profile $PROFILE --region $REGION
done

### 4️⃣ Delete IAM Roles created by Control Tower

for role in AWSControlTowerAdmin AWSControlTowerExecution AWSControlTowerCloudTrailRole; do
  echo "Deleting IAM role $role (if exists)"
  aws iam delete-role --role-name $role --profile $PROFILE || echo "$role not found"
done

### 5️⃣ Disable Security Services (GuardDuty, Security Hub, Macie)

echo "Disabling GuardDuty (if enabled)"
GD_DETECTOR=$(aws guardduty list-detectors --profile $PROFILE --region $REGION --query 'DetectorIds[0]' --output text)
if [ "$GD_DETECTOR" != "None" ]; then
  aws guardduty delete-detector --detector-id $GD_DETECTOR --profile $PROFILE --region $REGION
fi

echo "Disabling Security Hub (if enabled)"
aws securityhub disable-security-hub --profile $PROFILE --region $REGION || echo "Security Hub not enabled"

echo "Disabling Macie (if enabled)"
aws macie2 disable-macie --profile $PROFILE --region $REGION || echo "Macie not enabled"

echo "✅ Cleanup completed"


ROLE=AWSControlTowerCloudTrailRole
PROFILE=prod

# List attached policies
aws iam list-attached-role-policies --role-name $ROLE --profile $PROFILE

# Detach all attached policies (example)
aws iam detach-role-policy --role-name $ROLE --policy-arn arn:aws:iam::aws:policy/AdministratorAccess --profile $PROFILE

# Delete inline policies (if any)
aws iam list-role-policies --role-name $ROLE --profile $PROFILE
# If any inline policies:
aws iam delete-role-policy --role-name $ROLE --policy-name <policy-name> --profile $PROFILE

# Finally delete role
aws iam delete-role --role-name $ROLE --profile $PROFILE

