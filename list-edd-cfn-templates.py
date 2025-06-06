#!/usr/bin/env python3
"""
AWS CloudFormation Active Resources Inventory
Lists only ACTIVE stacks (us-east-1) and stack sets (global)
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import argparse
import csv
from datetime import datetime

# Configuration
VALID_STACK_STATUSES = [
    'CREATE_COMPLETE',
    'UPDATE_COMPLETE',
    'UPDATE_ROLLBACK_COMPLETE',
    'IMPORT_COMPLETE',
    'ROLLBACK_COMPLETE'
]

def get_boto3_session(profile_name=None, region='us-east-1'):
    """Initialize AWS session with optional profile"""
    try:
        if profile_name:
            return boto3.Session(profile_name=profile_name, region_name=region)
        return boto3.Session(region_name=region)
    except NoCredentialsError:
        print("Error: No AWS credentials found")
        exit(1)

def get_active_stacks(cf_client):
    """Retrieve all active stacks with pagination"""
    stacks = []
    paginator = cf_client.get_paginator('list_stacks')
    
    try:
        for page in paginator.paginate(StackStatusFilter=VALID_STACK_STATUSES):
            stacks.extend(page['StackSummaries'])
        return stacks
    except ClientError as e:
        print(f"AWS API Error: {e}")
        return []

def get_active_stack_sets(cf_client):
    """Retrieve all active stack sets with pagination"""
    stack_sets = []
    paginator = cf_client.get_paginator('list_stack_sets')
    
    try:
        for page in paginator.paginate(Status='ACTIVE'):
            stack_sets.extend(page['Summaries'])
        return stack_sets
    except ClientError as e:
        print(f"AWS API Error: {e}")
        return []

def generate_report_data(stacks, stack_sets):
    """Prepare data for CSV output"""
    report_data = []
    
    for stack in stacks:
        creation_time = stack.get('CreationTime', '')
        last_updated_time = stack.get('LastUpdatedTime', '')
        
        # Handle datetime objects
        creation_time = creation_time.isoformat() if isinstance(creation_time, datetime) else creation_time or 'N/A'
        last_updated_time = last_updated_time.isoformat() if isinstance(last_updated_time, datetime) else last_updated_time or 'N/A'
        
        report_data.append({
            'Type': 'Stack',
            'Name': stack['StackName'],
            'Status': stack['StackStatus'],
            'Region': 'us-east-1',
            'CreationTime': creation_time,
            'LastUpdatedTime': last_updated_time,
            'Description': stack.get('TemplateDescription', ''),
            'StackId': stack.get('StackId', '')
        })
    
    for stack_set in stack_sets:
        creation_time = stack_set.get('CreationTime', '')
        last_updated_time = stack_set.get('LastUpdatedTime', '')
        
        # Handle datetime objects
        creation_time = creation_time.isoformat() if isinstance(creation_time, datetime) else creation_time or 'N/A'
        last_updated_time = last_updated_time.isoformat() if isinstance(last_updated_time, datetime) else last_updated_time or 'N/A'
        
        report_data.append({
            'Type': 'StackSet',
            'Name': stack_set['StackSetName'],
            'Status': stack_set['Status'],
            'Region': 'Global',
            'CreationTime': creation_time,
            'LastUpdatedTime': last_updated_time,
            'Description': stack_set.get('Description', ''),
            'StackId': stack_set.get('StackSetId', '')
        })
    
    return report_data

def write_csv_report(data, filename):
    """Write data to CSV file"""
    fieldnames = [
        'Type', 'Name', 'Status', 'Region',
        'CreationTime', 'LastUpdatedTime', 
        'Description', 'StackId'
    ]
    
    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        return True
    except IOError as e:
        print(f"File Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Generate AWS CloudFormation active resources report',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--profile', help='AWS profile name')
    parser.add_argument('--output', default='active_cf_resources.csv',
                      help='Output CSV filename')
    args = parser.parse_args()

    # Initialize AWS clients
    session = get_boto3_session(args.profile)
    cf_client = session.client('cloudformation')

    print("Collecting active CloudFormation resources...")
    
    # Get data
    stacks = get_active_stacks(cf_client)
    stack_sets = get_active_stack_sets(cf_client)
    report_data = generate_report_data(stacks, stack_sets)

    # Write report
    if write_csv_report(report_data, args.output):
        print(f"\nSuccessfully generated report: {args.output}")
        print(f"- Active Stacks: {len(stacks)}")
        print(f"- Active StackSets: {len(stack_sets)}")
        print(f"- Total Resources: {len(report_data)}")
    else:
        print("\nFailed to generate report")

if __name__ == "__main__":
    main()
    
    
##########################

# AWS CloudFormation Active Resources Inventory

# A Python utility script that generates an inventory report of active AWS CloudFormation stacks and stack sets.

# ## Overview

# This script queries your AWS account to identify:
# - Active CloudFormation stacks in the us-east-1 region
# - Active CloudFormation stack sets (global)

# It then generates a CSV report containing details about these resources, including their names, statuses, creation times, and last updated times.

# ## Prerequisites

# - Python 3.x
# - AWS credentials configured (via AWS CLI, environment variables, or IAM role)
# - Required Python packages:
#   - boto3
#   - botocore

# ## Installation

# 1. Clone or download this repository
# 2. Install required dependencies:

# ```bash
# pip install boto3
# ```

# ## Usage

# Basic usage:

# ```bash
# python list-edd-cfn-templates.py
# ```

# This will generate a CSV file named `active_cf_resources.csv` in the current directory.

# ### Command-line Options

# - `--profile`: Specify an AWS profile name to use (optional)
# - `--output`: Specify the output CSV filename (default: `active_cf_resources.csv`)

# Example with options:

# ```bash
# python list-edd-cfn-templates.py --profile my-aws-profile --output my-report.csv
# ```

# ## Output

# The generated CSV file contains the following columns:

# - Type: Either "Stack" or "StackSet"
# - Name: Name of the stack or stack set
# - Status: Current status of the resource
# - Region: "us-east-1" for stacks, "Global" for stack sets
# - CreationTime: When the resource was created
# - LastUpdatedTime: When the resource was last updated
# - Description: Template description (if available)
# - StackId: The unique identifier for the resource

# ## Active Stack Statuses

# The script considers the following stack statuses as "active":
# - CREATE_COMPLETE
# - UPDATE_COMPLETE
# - UPDATE_ROLLBACK_COMPLETE
# - IMPORT_COMPLETE
# - ROLLBACK_COMPLETE

# ## Notes

# - The script only queries the us-east-1 region for stacks
# - Stack sets are queried globally
# - AWS credentials must have permissions to list CloudFormation stacks and stack sets