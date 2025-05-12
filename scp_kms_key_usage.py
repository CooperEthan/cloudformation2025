import boto3
import json
import argparse

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
        ]
    }

    try:
        response = org_client.create_policy(
            Content=json.dumps(scp_policy),
            Description="Enforces S3 KMS encryption",
            Name=policy_name,
            Type='SERVICE_CONTROL_POLICY'
        )
        policy_id = response['Policy']['PolicySummary']['Id']
        org_client.attach_policy(PolicyId=policy_id, TargetId=ou_id)
        print(f"✅ Success! Policy {policy_name} attached to OU {ou_id}")
        return policy_id
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ou", required=True, help="AWS Organizational Unit ID (e.g., ou-xxxx-xxxxxxxx)")
    parser.add_argument("--name", default="S3-KMS-Enforcement-SCP", help="SCP policy name")
    args = parser.parse_args()
    
    create_and_attach_scp_policy(args.ou, args.name)
    
    
    
    
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

# How to Run It
# Pass the OU ID as an argument when executing:
# Basic usage (required OU)
# python3 scp_kms_key_usage.py --ou ou-xxxx-xxxxxxxx

# With custom policy name
# python3 scp_kms_key_usage.py --ou ou-xxxx-xxxxxxxx --name "My-Custom-Policy-Name"


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



# ****Optionally we can add following policies******

            # # Commented-out rules (4-5) - will be stringified with /* */
            # """
            # {
            #     "Sid": "DenyNonPrefixedKMSKeysForCreate",
            #     "Effect": "Deny",
            #     "Action": "s3:CreateBucket",
            #     "Resource": "*",
            #     "Condition": {
            #         "StringNotLikeIfExists": {
            #             "s3:x-amz-server-side-encryption-aws-kms-key-id": "arn:aws:kms:*:*:key/iv-*"
            #         }
            #     }
            # },
            # {
            #     "Sid": "DenyNonPrefixedKMSKeysForUpdates",
            #     "Effect": "Deny",
            #     "Action": "s3:PutBucketEncryption",
            #     "Resource": "*",
            #     "Condition": {
            #         "StringNotLikeIfExists": {
            #             "s3:x-amz-server-side-encryption-aws-kms-key-id": "arn:aws:kms:*:*:key/iv-*"
            #         }
            #     }
            # }
            # """