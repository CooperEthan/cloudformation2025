# AWS CloudFormation Active Resources Inventory

A Python utility script that generates an inventory report of active AWS CloudFormation stacks and stack sets.

## Overview

This script queries your AWS account to identify:
- Active CloudFormation stacks in the us-east-1 region
- Active CloudFormation stack sets (global)

It then generates a CSV report containing details about these resources, including their names, statuses, creation times, and last updated times.

## Prerequisites

- Python 3.x
- AWS credentials configured (via AWS CLI, environment variables, or IAM role)
- Required Python packages:
  - boto3
  - botocore

## Installation

1. Clone or download this repository
2. Install required dependencies:

```bash
pip install boto3
```

## Usage

Basic usage:

```bash
python list-edd-cfn-templates.py
```

This will generate a CSV file named `active_cf_resources.csv` in the current directory.

### Command-line Options

- `--profile`: Specify an AWS profile name to use (optional)
- `--output`: Specify the output CSV filename (default: `active_cf_resources.csv`)

Example with options:

```bash
python list-edd-cfn-templates.py --profile my-aws-profile --output my-report.csv
```

## Output

The generated CSV file contains the following columns:

- Type: Either "Stack" or "StackSet"
- Name: Name of the stack or stack set
- Status: Current status of the resource
- Region: "us-east-1" for stacks, "Global" for stack sets
- CreationTime: When the resource was created
- LastUpdatedTime: When the resource was last updated
- Description: Template description (if available)
- StackId: The unique identifier for the resource

## Active Stack Statuses

The script considers the following stack statuses as "active":
- CREATE_COMPLETE
- UPDATE_COMPLETE
- UPDATE_ROLLBACK_COMPLETE
- IMPORT_COMPLETE
- ROLLBACK_COMPLETE

## Notes

- The script only queries the us-east-1 region for stacks
- Stack sets are queried globally
- AWS credentials must have permissions to list CloudFormation stacks and stack sets

## License

[Specify your license information here]