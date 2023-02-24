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
    table_of_contents = '{toc:printable=true|style=disc}'

    kickoff_section = f'h1. Kickoff\n- _Sprint goals:_ {sprint_goals}\n'

    # Define the Sprint Backlog table
    sprint_backlog_table = '||Sprint Backlog Item||Live in Production||\n'
    for issue in issues:
        issue_key = html.escape(issue["key"])
        issue_link = f'https://industrydive.atlassian.net/browse/{issue_key}'
        issue_status = html.escape(issue["fields"]["status"]["name"])
        sprint_backlog_table += f'|[{issue_link}]|{"YES" if issue_status == "Done" else "NO"}|\n'

    # Define the Developer Demonstration section
    developer_demo_dicts = []
    for issue in issues:
        issue_key = html.escape(issue["key"])
        issue_title = html.escape(issue["fields"]["summary"])
        assigned_to = html.escape(issue["fields"]["assignee"]["displayName"])
        developer_demo_dicts.append({
            'issue_key': issue_key,
            'issue_title': issue_title,
            'assigned_to': assigned_to,
        })
    developer_demo_dicts.sort(key=lambda x: x['assigned_to'])

    developer_demo_section = ''
    for issue in developer_demo_dicts:
        description = "_Enter a description here..._"
        developer_demo_section += f'h3. {issue["issue_title"]}\n'
        developer_demo_section += f'Presented by: @{issue["assigned_to"]}\n'
        developer_demo_section += f'Completed by: @{issue["assigned_to"]}\n'
        developer_demo_section += f'Description: {description}\n'
        developer_demo_section += 'Demo: \n'
        developer_demo_section += html.escape('Q&A: \n\n')

    # Define the full page HTML
    page_html = f'{table_of_contents}\n'
    page_html+= f'{kickoff_section}{sprint_backlog_table}\n'
    page_html += f'h1. Developer Demonstration\n{developer_demo_section}'
    page_html += f'h2. Additional Topics\n- N/A\n'
    page_html += f'h1. Roadmap Review and Product Backlog\n'
    page_html += f'- Presented by @Erin Erikson\n- Product Roadmap:\n- Product Backlog Top Items:\n'
    page_html += f'h1. Q&A\n'
    page_html += f'h1. Action Items\n'

    data = {
        'type': 'page',
        'title': page_title,
        'ancestors': [{'id':3517841558}],
        'space': {'key':'TECH'},
        'body': {
            'storage':{
                'value': page_html,
                'representation':'wiki',
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