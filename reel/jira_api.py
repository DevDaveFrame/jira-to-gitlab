import requests
import os
import base64

# Get environment variables
email = os.environ['JIRA_EMAIL']
token = os.environ['JIRA_TOKEN']
base_url = os.environ['JIRA_URL']
board_id = os.environ['JIRA_BOARD_ID']


def get_issues(sprint_id, limit=100, page=1):
    """
    Get all issues for a project
    """
    encoded_token = encode_token()
    url = f'{base_url}/rest/agile/1.0/board/{board_id}/sprint/{sprint_id}/issue?page={page}&per_page={limit}'
    headers = {
        'Authorization': f'Basic {encoded_token}',
        'Accepts': 'application/json',
    }
    response = requests.get(url, headers=headers)
    return response.json()


def encode_token():
    """
    base64 encode the email:token
    """
    # base64 encode the token
    encoded_token = base64.b64encode(f'{email}:{token}')
    return f'Basic {encoded_token}'
