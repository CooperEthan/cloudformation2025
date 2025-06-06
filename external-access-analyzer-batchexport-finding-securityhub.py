import boto3
import json

def setup_integration():
    # Initialize clients
    session = boto3.Session()
    iam = session.client('iam')
    events = session.client('events')
    securityhub = session.client('securityhub')
    
    # 1. Create IAM Role
    try:
        role = iam.create_role(
            RoleName='EventBridgeToSecurityHubRole',
            AssumeRolePolicyDocument=json.dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "events.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            })
        )
        
        iam.put_role_policy(
            RoleName='EventBridgeToSecurityHubRole',
            PolicyName='SecurityHubAccessPolicy',
            PolicyDocument=json.dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Action": "securityhub:BatchImportFindings",
                    "Resource": "*"
                }]
            })
        )
    except iam.exceptions.EntityAlreadyExistsException:
        print("Role already exists")
    
    # 2. Create EventBridge Rule
    try:
        rule = events.put_rule(
            Name='AccessAnalyzerToSecurityHub',
            Description='Forwards IAM Access Analyzer findings to Security Hub',
            EventPattern=json.dumps({
                "source": ["aws.accessanalyzer"],
                "detail-type": ["Access Analyzer Finding"]
            }),
            State='ENABLED'
        )
        
        events.put_targets(
            Rule='AccessAnalyzerToSecurityHub',
            Targets=[{
                'Id': 'SecurityHubTarget',
                'Arn': f'arn:aws:securityhub:{session.region_name}:{session.client("sts").get_caller_identity()["Account"]}:hub/default',
                'RoleArn': role['Role']['Arn'],
                'InputTransformer': {
                    'InputPathsMap': {
                        'findingId': '$.detail.findingId',
                        'resourceType': '$.detail.resourceType',
                        'principal': '$.detail.principal',
                        'status': '$.detail.status',
                        'createdAt': '$.detail.createdAt',
                        'findingType': '$.detail.findingType'
                    },
                    'InputTemplate': json.dumps({
                        "Findings": [{
                            "SchemaVersion": "2018-10-08",
                            "ProductArn": f"arn:aws:securityhub:{session.region_name}::product/aws/access-analyzer",
                            "GeneratorId": "access-analyzer",
                            "Id": "<findingId>",
                            "CreatedAt": "<createdAt>",
                            "UpdatedAt": "<createdAt>",
                            "Severity": {"Label": "MEDIUM"},
                            "Title": "Access Analyzer <findingType> finding for <resourceType>",
                            "Description": "Principal <principal> has potential access issue",
                            "Resources": [{
                                "Type": "<resourceType>",
                                "Id": "<findingId>"
                            }],
                            "FindingProviderFields": {
                                "Severity": {"Label": "MEDIUM"},
                                "Types": ["Software and Configuration Checks/AWS Security Best Practices"]
                            }
                        }]
                    })
                }
            }]
        )
    except events.exceptions.ResourceAlreadyExistsException:
        print("Rule already exists")

if __name__ == "__main__":
    setup_integration()