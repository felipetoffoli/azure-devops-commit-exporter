from azure.devops.connection import Connection
from azure.devops.v7_1.git.models import GitQueryCommitsCriteria
from msrest.authentication import BasicAuthentication
from datetime import datetime, timedelta
import csv
import os
import boto3


TYPE_EXPORT_FILE = os.environ.get("TYPE_EXPORT_FILE", "FILE")  
S3_ENDPOINT_URL = os.environ.get("S3_ENDPOINT_URL")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY")
S3_PORT = os.environ.get("S3_PORT", "443") 


AZURE_PERSONAL_TOKEN = os.environ.get("AZURE_PERSONAL_TOKEN")
AZURE_ORGANIZATION_URL = os.environ.get("AZURE_ORGANIZATION_URL")
GIT_DATE_FROM = os.environ.get("GIT_DATE_FROM")
GIT_AUTHOR_EMAIL = os.environ.get("GIT_AUTHOR_EMAIL")


credentials = BasicAuthentication('', AZURE_PERSONAL_TOKEN)
connection = Connection(base_url=AZURE_ORGANIZATION_URL, creds=credentials)
connection.api_version = "7.1"  



def subtract_day(date_str, day_number: int):
    """Subtracts a specified number of days from the given date string."""
    search_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    search_date = search_date - timedelta(days=day_number)
    search_date_str = search_date.strftime('%Y-%m-%d')
    return search_date_str


def get_commits_by_email_and_date(project_name, email, GIT_DATE_FROM):
    git_client = connection.clients.get_git_client()
    
    repositories = git_client.get_repositories(project=project_name)

    project_data = {}
    project_data[project_name] = {}

    for repo in repositories:
        
        search_date_str = subtract_day(GIT_DATE_FROM, 1)
       
        search_criteria = GitQueryCommitsCriteria(
            author=email,
            from_date=search_date_str
        )

        try:
            commits_list = git_client.get_commits(
                repository_id=repo.id,
                search_criteria=search_criteria,
                project=project_name
            )
            
            commits = []
            if commits_list:
                for commit in commits_list:
                    commit_data = {
                        "Commit ID": commit.commit_id,
                        "Author": commit.author.name,
                        "Date": commit.author.date,
                        "Message": commit.comment
                    }
                    commits.append(commit_data)
            
            
            commits = sorted(commits, key=lambda x: x['Date'])
            
            project_data[project_name][repo.name] = commits

        except Exception as e:
            print(f"  Error fetching commits: {e}")
            project_data[project_name][repo.name] = []
    return project_data


def get_commits_alls_projects_from_date(GIT_AUTHOR_EMAIL, GIT_DATE_FROM):
    
    core_client = connection.clients.get_core_client()
    projects = core_client.get_projects()
    all_projects_data = {}
    
    for project in projects:
        project_data = get_commits_by_email_and_date(project.name, GIT_AUTHOR_EMAIL, GIT_DATE_FROM)
        
        
        has_commits = False
        for repo, commits in project_data[project.name].items():
            if commits:
                has_commits = True
                break
        
        if has_commits:
            all_projects_data.update(project_data)
    return all_projects_data

def convert_dict_to_csv(data):
    """Converts the dictionary to CSV format."""
    csv_data = "Project,Repository,Commit ID,Author,Date,Message\n"
    for project, repos in data.items():
        for repo, commits in repos.items():
            for commit in commits:
                csv_data += f"{project},{repo},{commit['Commit ID']},{commit['Author']},{commit['Date']},{commit['Message']}\n"
    return csv_data

def export_csv_file(csv_data, filename="commits.csv"):
    """Exports the CSV data to a file."""
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        csvfile.write(csv_data)
    print(f"CSV data exported to {filename}")
import os
import csv
from datetime import datetime

def save_to_file(data):
    """Saves commit data to a CSV file in the 'file' directory, creating the directory if it doesn't exist, and returns the file path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    
    file_directory = "file"
    if not os.path.exists(file_directory):
        os.makedirs(file_directory)
    
    filename = f"commits_{timestamp}.csv"
    filepath = os.path.join(file_directory, filename)  
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Project", "Repository", "Commit ID", "Author", "Date", "Message"])  
        for project, repos in data.items():
            for repo, commits in repos.items():
                for commit in commits:
                    writer.writerow([project, repo, commit['Commit ID'], commit['Author'], commit['Date'], commit['Message']])
    print(f"Data saved to {filepath}")
    return filepath

def upload_to_s3(filepath):
    """Uploads a file to MinIO/S3."""
    if not all([S3_ENDPOINT_URL, S3_BUCKET_NAME, S3_ACCESS_KEY, S3_SECRET_KEY]):
        raise ValueError("Missing S3/MinIO configuration environment variables.")

    
    endpoint_url = S3_ENDPOINT_URL
    if not endpoint_url.startswith(("http://", "https://")):
        endpoint_url = f"http://{endpoint_url}"

    
    if S3_PORT and S3_PORT != "443":
        endpoint_url = f"{endpoint_url}:{S3_PORT}"

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY
    )

    filename = os.path.basename(filepath)

    try:
        with open(filepath, "rb") as file_obj:
            s3.upload_fileobj(file_obj, S3_BUCKET_NAME, filename)
        print(f"Access to {S3_BUCKET_NAME}/buckets/{S3_BUCKET_NAME}/browse/{filename}")
        
    except Exception as e:
        print(f"Error uploading to S3: {e}")


all_commits = get_commits_alls_projects_from_date(GIT_AUTHOR_EMAIL, GIT_DATE_FROM)


for project, repos in all_commits.items():
    print(f"Project: {project}")
    for repo, commits in repos.items():
        if commits:
            print(f"  Repository: {repo}")
            for commit in commits:
                print(f"    Commit ID: {commit['Commit ID']}")
                print(f"    Author: {commit['Author']}")
                print(f"    Date: {commit['Date']}")
                print(f"    Message: {commit['Message']}")
                print("    " + "-" * 30)
            print("  " + "=" * 30)

if TYPE_EXPORT_FILE.upper() == "S3":
    csv_filepath = save_to_file(all_commits)  
    upload_to_s3(csv_filepath)  
else:  
    save_to_file(all_commits)