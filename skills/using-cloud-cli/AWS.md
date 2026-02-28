# AWS Patterns

## S3

```bash
# List buckets
aws s3 ls

# List objects
aws s3 ls s3://bucket/prefix/

# Copy
aws s3 cp local_file s3://bucket/path/
aws s3 cp s3://bucket/path/file .

# Sync
aws s3 sync local_dir/ s3://bucket/path/
aws s3 sync s3://bucket/path/ local_dir/

# Remove
aws s3 rm s3://bucket/path/file
aws s3 rm s3://bucket/path/ --recursive
```

## EC2

```bash
# List instances
aws ec2 describe-instances \
  --query 'Reservations[].Instances[].[InstanceId,State.Name,PublicIpAddress]' \
  --output table

# Start/Stop
aws ec2 start-instances --instance-ids i-xxxxx
aws ec2 stop-instances --instance-ids i-xxxxx

# Create instance
aws ec2 run-instances \
  --image-id ami-xxxxx \
  --instance-type t3.micro \
  --key-name my-key \
  --security-group-ids sg-xxxxx \
  --subnet-id subnet-xxxxx

# Dry run
aws ec2 run-instances --dry-run ...
```

## Lambda

```bash
# List functions
aws lambda list-functions --query 'Functions[].FunctionName' --output table

# Invoke
aws lambda invoke --function-name FUNC output.json
cat output.json

# Update code
aws lambda update-function-code \
  --function-name FUNC \
  --zip-file fileb://function.zip

# View logs
aws logs filter-log-events \
  --log-group-name /aws/lambda/FUNC \
  --start-time $(date -d '1 hour ago' +%s000)
```

## ECS

```bash
# List clusters
aws ecs list-clusters

# List services
aws ecs list-services --cluster CLUSTER

# Update service (force deploy)
aws ecs update-service \
  --cluster CLUSTER \
  --service SERVICE \
  --force-new-deployment

# View tasks
aws ecs list-tasks --cluster CLUSTER --service-name SERVICE
```

## IAM

```bash
# List roles
aws iam list-roles --query 'Roles[].RoleName' --output table

# Get user
aws sts get-caller-identity

# List attached policies
aws iam list-attached-role-policies --role-name ROLE
```

## Common Flags

| Flag                         | Purpose             |
| ---------------------------- | ------------------- |
| `--region REGION`            | Explicit region     |
| `--output json\|table\|text` | Output format       |
| `--query 'JMESPath'`         | Filter results      |
| `--profile PROFILE`          | Named profile       |
| `--dry-run`                  | Preview (EC2, etc.) |

## JMESPath Examples

```bash
# Get instance IDs
--query 'Reservations[].Instances[].InstanceId'

# Filter by tag
--query 'Reservations[].Instances[?Tags[?Key==`Name` && Value==`web`]]'

# Multiple fields
--query 'Reservations[].Instances[].[InstanceId,State.Name]'

# First result
--query 'Reservations[0].Instances[0].InstanceId'
```
