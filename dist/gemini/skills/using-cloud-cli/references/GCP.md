# GCP Patterns

## BigQuery

```bash
# Cost estimation
bq query --dry_run --use_legacy_sql=false \
  'SELECT * FROM `project.dataset.table` WHERE date > "2024-01-01"'

# Standard query
bq query --use_legacy_sql=false --format=json \
  'SELECT col1, col2 FROM `project.dataset.table` LIMIT 100'

# Save to table
bq query --use_legacy_sql=false \
  --destination_table=project:dataset.result \
  'SELECT ...'

# Export to GCS
bq extract --destination_format=NEWLINE_DELIMITED_JSON \
  project:dataset.table gs://bucket/path/*.json
```

### Cost Optimization

- Always `--dry_run` first to estimate bytes scanned
- Avoid `SELECT *` - specify columns
- Use partitioned tables with partition filters
- Use clustered tables for frequent filter columns
- `LIMIT` doesn't reduce scan cost (use in WHERE)

## Cloud Storage

```bash
# List
gsutil ls gs://bucket/path/

# Copy
gsutil cp local_file gs://bucket/path/
gsutil cp -r local_dir/ gs://bucket/path/

# Sync (like rsync)
gsutil rsync -r local_dir/ gs://bucket/path/

# Download
gsutil cp gs://bucket/path/file .
gsutil cp -r gs://bucket/path/ local_dir/
```

## Compute Engine

```bash
# List instances
gcloud compute instances list --format="table(name,zone,status,networkInterfaces[0].accessConfigs[0].natIP)"

# Create
gcloud compute instances create NAME \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --image-family=debian-12 \
  --image-project=debian-cloud

# SSH
gcloud compute ssh INSTANCE --zone=ZONE

# Stop/Start
gcloud compute instances stop INSTANCE --zone=ZONE
gcloud compute instances start INSTANCE --zone=ZONE
```

## Cloud Run

```bash
# Deploy
gcloud run deploy SERVICE \
  --image=gcr.io/PROJECT/IMAGE \
  --region=us-central1 \
  --allow-unauthenticated

# List services
gcloud run services list --format=json

# View logs
gcloud run services logs read SERVICE --region=REGION
```

## IAM

```bash
# List service accounts
gcloud iam service-accounts list --format=json

# Create service account
gcloud iam service-accounts create NAME --display-name="Description"

# Add role binding
gcloud projects add-iam-policy-binding PROJECT \
  --member="serviceAccount:SA@PROJECT.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"
```

## Common Flags

| Flag                      | Purpose                 |
| ------------------------- | ----------------------- |
| `--project=PROJECT`       | Explicit project        |
| `--format=json`           | JSON output for parsing |
| `--quiet`                 | No prompts (automation) |
| `--filter="name:pattern"` | Server-side filter      |
