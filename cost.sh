# Bash script to check AWS Config + Kinesis in ALL regions
for region in $(aws ec2 describe-regions --query "Regions[].RegionName" --output text); do
  echo "Checking region: $region"
  aws configservice describe-configuration-recorders --region $region
  aws configservice describe-delivery-channels --region $region
  aws configservice describe-aggregation-authorizations --region $region
  aws kinesis list-streams --region $region
  aws firehose list-delivery-streams --region $region
done

