import requests
import os
import json
import html
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

def create_review_agenda(sprint_id):
    """
    Create a review agenda for a sprint
    """
    encoded_token = encode_token()
    url = f'{base_url}/wiki/rest/api/content'
    headers = {
        'Authorization': f'Basic {encoded_token}',
        'Content-Type': 'application/json',
    }

    page_title = f'Team Astra Sprint Review {sprint_id}'
    response = get_issues(sprint_id)
    issues = response['issues']

    # Define the sprint goals
    sprint_goals = "Finish all the features scheduled for this sprint."

    # Define the table of contents widget
    table_of_contents = '<ac:structured-macro ac:name="toc">\n<ac:parameter ac:name="style">disc</ac:parameter>\n</ac:structured-macro>\n'

    kickoff_section = f'<h1>Kickoff</h1>\n<ul><li><em>Sprint goals: {sprint_goals}</em></li></ul>\n'

    # Define the Sprint Backlog table
    sprint_backlog_table = '<table>\n<tr>\n<th>Sprint Backlog Item</th>\n<th>Live in Production</th>\n</tr>\n'
    for issue in issues:
        issue_key = html.escape(issue["key"])
        issue_link = f'https://industrydive.atlassian.net/browse/{issue_key}'
        issue_status = html.escape(issue["fields"]["status"]["name"])
        sprint_backlog_table += f'<tr>\n<td><a href="{issue_link}">{issue_link}</a></td>\n<td>{"YES" if issue_status == "Done" else "NO"}</td>\n</tr>\n'
    sprint_backlog_table += '</table>\n'

    # Define the Developer Demonstration section
    developer_demo_section = ''
    for issue in issues:
        issue_title = html.escape(issue["fields"]["summary"])
        assigned_to = html.escape(issue["fields"]["assignee"]["displayName"])
        description = "*Enter a description here.*"
        developer_demo_section += f'<h3>{issue_title}</h3>'
        developer_demo_section += f'Presented by: @{assigned_to}\n\n'
        developer_demo_section += f'Completed by: @{assigned_to}\n\n'
        developer_demo_section += f'Description: {description}\n\n'
        developer_demo_section += 'Demo: \n\n'
        developer_demo_section += html.escape('Q&A: \n\n')

    # Define the full page HTML
    page_html = f'{table_of_contents}{kickoff_section}{sprint_backlog_table}\n<h1>Developer Demonstration</h1>\n{developer_demo_section}'

    data = {
        'type': 'page',
        'title': page_title,
        'ancestors': [{'id':3517841558}],
        'space': {'key':'TECH'},
        'body': {
            'storage':{
                'value': page_html,
                'representation':'storage',
                'content-type':'text/html'
            }
        }
    }

    return requests.post(url=url, data=json.dumps(data), headers=headers)


def encode_token():
    """
    base64 encode the email:token
    """
    # base64 encode the string
    encoded_token = base64.b64encode(f'{email}:{token}'.encode('utf-8'))
    return encoded_token.decode('utf-8')