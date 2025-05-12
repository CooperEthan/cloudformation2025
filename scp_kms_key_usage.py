import boto3
import json

def create_and_attach_scp_policy(ou_id, policy_name):
    """
    Creates and attaches an SCP policy that enforces:
    - Mandatory KMS encryption for new S3 buckets
    - Prevention of encryption removal for existing buckets
    """
    org_client = boto3.client('organizations')
    
    # SCP Policy Document (no tagging conditions)
    scp_policy = {
        "Version": "2012-10-17",
        "Statement": [
            # Active enforcement rules
            {
                "Sid": "DenyUnencryptedBucketCreation",
                "Effect": "Deny",
                "Action": "s3:CreateBucket",
                "Resource": "*",
                "Condition": {
                    "Null": {
                        "s3:x-amz-server-side-encryption": "true"
                    }
                }
            },
            {
                "Sid": "RequireKMSEncryption",
                "Effect": "Deny",
                "Action": "s3:CreateBucket",
                "Resource": "*",
                "Condition": {
                    "StringNotEqualsIfExists": {
                        "s3:x-amz-server-side-encryption": "aws:kms"
                    }
                }
            },
            {
                "Sid": "PreventEncryptionRemoval",
                "Effect": "Deny",
                "Action": "s3:PutBucketEncryption",
                "Resource": "*",
                "Condition": {
                    "StringNotEquals": {
                        "s3:x-amz-server-side-encryption": "aws:kms"
                    }
                }
            },
            # Commented-out rules (4-5) - will be stringified with /* */
            """
            {
                "Sid": "DenyNonPrefixedKMSKeysForCreate",
                "Effect": "Deny",
                "Action": "s3:CreateBucket",
                "Resource": "*",
                "Condition": {
                    "StringNotLikeIfExists": {
                        "s3:x-amz-server-side-encryption-aws-kms-key-id": "arn:aws:kms:*:*:key/iv-*"
                    }
                }
            },
            {
                "Sid": "DenyNonPrefixedKMSKeysForUpdates",
                "Effect": "Deny",
                "Action": "s3:PutBucketEncryption",
                "Resource": "*",
                "Condition": {
                    "StringNotLikeIfExists": {
                        "s3:x-amz-server-side-encryption-aws-kms-key-id": "arn:aws:kms:*:*:key/iv-*"
                    }
                }
            }
            """
        ]
    }

    try:
        # Create and attach policy
        response = org_client.create_policy(
            Content=json.dumps(scp_policy),
            Description="Enforces S3 KMS encryption (no tagging dependencies)",
            Name=policy_name,
            Type='SERVICE_CONTROL_POLICY'
        )
        
        policy_id = response['Policy']['PolicySummary']['Id']
        org_client.attach_policy(PolicyId=policy_id, TargetId=ou_id)
        
        print(f"✅ Successfully attached policy {policy_name} to OU {ou_id}")
        print(f"Policy ID: {policy_id}")
        return policy_id
        
    except org_client.exceptions.DuplicatePolicyException:
        print(f"⚠️ Policy {policy_name} already exists. Skipping creation.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

# Configuration
OU_ID = 'ou-xxxx-xxxxxxxx'  # Replace with your target OU ID
POLICY_NAME = 'S3-KMS-Enforcement-SCP'  # Customize policy name

if __name__ == "__main__":
    create_and_attach_scp_policy(OU_ID, POLICY_NAME)
    
    
    
    
# # AWS S3 Encryption Enforcement SCP Attacher

# ## 📝 Description
# Python script to deploy an AWS Service Control Policy (SCP) that enforces:
# - **Mandatory KMS encryption** for all new S3 buckets
# - **Prevention of encryption removal** for existing buckets

# ## 🚀 Quick Start

# ### Prerequisites
# - AWS Organizations enabled
# - Python 3.6+
# - boto3 (`pip install boto3`)
# - IAM permissions:
#   ```json
#   {
#     "Version": "2012-10-17",
#     "Statement": [
#       {
#         "Effect": "Allow",
#         "Action": [
#           "organizations:CreatePolicy",
#           "organizations:AttachPolicy"
#         ],
#         "Resource": "*"
#       }
#     ]
#   }

## Edit script variables:
# OU_ID = 'ou-xxxx-xxxxxxxx'  # Replace with target OU ID
# POLICY_NAME = 'S3-KMS-Enforcement-SCP'  # Custom policy name

# 3.Execute:
#python3 attach_scp.py


# Propagation
# Policy changes may take up to 1 hour to fully propagate

# Verify with: 
# aws organizations list-policies-for-target --target-id ou-xxxx-xxxxxxxx --filter SERVICE_CONTROL_POLICY


# 🚨 Rollback
# Detach policy if needed:
#     aws organizations detach-policy \
#   --policy-id p-xxxxxxxx \
#   --target-id ou-xxxx-xxxxxxxx


# Best Practices
# Test in non-production OUs first

# Monitor with AWS Config Rules: