
# azure-devops-commit-exporter

Docker image that connects to Azure DevOps, retrieves **your** commits across **all** repositories since a given date, and exports results as CSV (locally or to S3/MinIO).

## Objective
This tool automates the process of gathering your Git commits from every project and repository in an Azure DevOps organization, filtered by author and date, and outputs them in a timestamped CSV for reporting or archival.

## Features
- Scan **all** Azure DevOps projects and repositories  
- Filter commits by your email and a starting date  
- Export results to a timestamped CSV file  
- Optionally upload the CSV to an S3-compatible endpoint (MinIO, AWS S3)

## Supported Tags
- `latest` (Python 3.8, azure-devops v7.1 SDK)

## Environment Variables

| Variable                  | Default      | Required | Description                                                                                 |
|---------------------------|--------------|----------|---------------------------------------------------------------------------------------------|
| `AZURE_PERSONAL_TOKEN`    | ―            | yes      | Personal access token for Azure DevOps API authentication.                                  |
| `AZURE_ORGANIZATION_URL`  | ―            | yes      | Base URL of the Azure DevOps organization (e.g. `https://dev.azure.com/your-org`).          |
| `GIT_AUTHOR_EMAIL`        | ―            | yes      | Your email address to filter the commits.                                                  |
| `GIT_DATE_FROM`           | ―            | yes      | Starting date (YYYY-MM-DD) to search commits from (inclusive).                              |
| `TYPE_EXPORT_FILE`        | `FILE`       | no       | Export target: `FILE` (local) or `S3`.                                                      |
| `S3_ENDPOINT_URL`         | ―            | if TYPE_EXPORT_FILE=S3 | Endpoint for S3-compatible storage (e.g. `minio.local`).                       |
| `S3_BUCKET_NAME`          | ―            | if TYPE_EXPORT_FILE=S3 | Target bucket name.                                                                      |
| `S3_ACCESS_KEY`           | ―            | if TYPE_EXPORT_FILE=S3 | S3 access key.                                                                           |
| `S3_SECRET_KEY`           | ―            | if TYPE_EXPORT_FILE=S3 | S3 secret key.                                                                           |
| `S3_PORT`                 | `443`        | no       | Port for the S3 endpoint (only if not 443).                                                |

## Usage

### Pull the image
```bash
docker pull your-dockerhub-user/azure-devops-commit-exporter:latest
```

### Run locally and write CSV to container volume
```bash
docker run --rm \
  -e AZURE_PERSONAL_TOKEN=${AZURE_PERSONAL_TOKEN} \
  -e AZURE_ORGANIZATION_URL=${AZURE_ORGANIZATION_URL} \
  -e GIT_AUTHOR_EMAIL="seu.email@exemplo.com" \
  -e GIT_DATE_FROM="2023-01-01" \
  -v $(pwd)/output:/app/file \
  your-dockerhub-user/azure-devops-commit-exporter:latest
```
- CSV files will be created under the mounted `output` directory.

### Run and upload to S3/MinIO
```bash
docker run --rm \
  -e TYPE_EXPORT_FILE="S3" \
  -e AZURE_PERSONAL_TOKEN=${AZURE_PERSONAL_TOKEN} \
  -e AZURE_ORGANIZATION_URL=${AZURE_ORGANIZATION_URL} \
  -e GIT_AUTHOR_EMAIL="seu.email@exemplo.com" \
  -e GIT_DATE_FROM="2023-01-01" \
  -e S3_ENDPOINT_URL="minio.local" \
  -e S3_PORT="9000" \
  -e S3_BUCKET_NAME="my-bucket" \
  -e S3_ACCESS_KEY=${MINIO_ACCESS_KEY} \
  -e S3_SECRET_KEY=${MINIO_SECRET_KEY} \
  your-dockerhub-user/azure-devops-commit-exporter:latest
```

## Output
- **Local file mode**: CSV saved to `/app/file/commits_<timestamp>.csv`
- **S3 mode**: CSV uploaded to `<S3_BUCKET_NAME>/<filename>`

## Logging
Output is printed to `stdout`, including:
- Projects, repositories, commits found  
- Export status or S3 upload URL  

## Building the image

```bash
docker build -t your-dockerhub-user/azure-devops-commit-exporter:latest .
```

Ensure you have a `Dockerfile` in the project root. A minimal example:

```dockerfile
FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
CMD ["python", "app.py"]
```

## Author

**Felipe Toffoli Martins**  
DevOps | AWS | SRE | Python | Fullstack  
[LinkedIn](https://www.linkedin.com/in/felipetoffoli/)

## License
MIT
