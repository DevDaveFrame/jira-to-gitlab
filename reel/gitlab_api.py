import requests
import json
import os
import pprint
import zipfile
pp = pprint.PrettyPrinter(indent=4)
# Get environment variables
token = os.environ['GITLAB_TOKEN']
base_url = os.environ['GITLAB_URL']
project_id = os.environ['GITLAB_PROJECT_ID']
ci_job_token = os.environ['CI_JOB_TOKEN']


def trigger_pipeline():
    """
    https://docs.gitlab.com/ee/ci/triggers/
    https://gitlab.com/industrydive/divesite/-/settings/ci_cd#js-pipeline-triggers
    """
    url = f'{base_url}/api/v4/projects/{project_id}/trigger/pipeline?token={ci_job_token}ref=ENGB-174-test-failure-stats'
    url = 'https://gitlab.com/api/v4/projects/16877012/merge_requests/7709/pipelines'
    headers = {'Private-Token': token}
    print(f'{url=}')
    r = requests.post(url, headers)
    print(f'{r=}')
    import pdb; pdb.set_trace()

    print(f'{r.json=}')


def save_artifacts(project_id, token, job_id, save_path):
    url = f'{base_url}/api/v4/projects/{project_id}/jobs/{job_id}/artifacts'
    headers = {'Private-Token': token}
    print(f'{url=}')
    r = requests.get(url, headers=headers)
    path_to_zip_file = f'{save_path}/artifacts.zip'
    with open(path_to_zip_file, 'wb') as zip_ref:
        zip_ref.write(r.content)
    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall(f'{save_path}')

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

def get_last_n_job_artificats(status=None, name='Selenium tests', n=50):
    print(f'{n=}')
    print(f'{status=}')
    stored_jobs = []
    page = 1
    while len(stored_jobs) < n:
        print(f'Getting page {page}')
        jobs = get_jobs(project_id, token, limit=100, page=page)
        print(f'Got {len(jobs)} jobs')
        for job in jobs:
            print(f'{job["status"]=}')
            if job['name'] == name:
                if status and job['status'] == status:
                    stored_jobs.append(job)
                elif not status:
                    stored_jobs.append(job)
        page += 1
    cwd = os.getcwd()
    for job in stored_jobs:
        pipeline_created_at = job['pipeline']['created_at']
        sha8 = job['pipeline']['sha'][:8]
        save_path = f'artifacts/{pipeline_created_at}-{sha8}'
        os.makedirs(save_path, exist_ok=True)
        with open(f'{save_path}/job.json', "w") as outfile:
            json.dump(job, outfile, indent=True)

        save_artifacts(project_id, token, job['id'], save_path)
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
