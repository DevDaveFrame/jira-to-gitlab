import requests
import json
import os

# Get environment variables
token = os.environ['GITLAB_TOKEN']
base_url = os.environ['GITLAB_URL']
project_id = os.environ['GITLAB_PROJECT_ID']


def get_jobs(project_id, token, limit=100, page=1):
    """
    Get all jobs for a project
    """
    url = f'{base_url}/api/v4/projects/{project_id}/jobs?page={page}&per_page={limit}'
    headers = {'Private-Token': token}
    response = requests.get(url, headers=headers)
    return response.json()


def get_last_n_jobs(status=None, name='Selenium tests', n=50):
    """
    Get the last 100 failed selenium jobs for a project
    """

    stored_jobs = []
    page = 1
    while len(stored_jobs) < n:
        print(f'Getting page {page}')
        jobs = get_jobs(project_id, token, limit=100, page=page)
        print(f'Got {len(jobs)} jobs')
        for job in jobs:
            if job['name'] == name:
                if status and job['status'] == status:
                    stored_jobs.append(job)
                elif not status:
                    stored_jobs.append(job)
        page += 1
    return stored_jobs


def save_jobs(stored_jobs, output_file):
    """
    Save the failed jobs to a file
    """
    with open(output_file, 'w') as f:
        json.dump(stored_jobs, f)


def create_mr(project_id, token, title, description, source_branch, target_branch):
    """
    Create a merge request
    """
    url = f'{base_url}/api/v4/projects/{project_id}/merge_requests'
    headers = {'Private-Token': token}
    data = {
        'title': title,
        'description': description,
        'source_branch': source_branch,
        'target_branch': target_branch,
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json()
