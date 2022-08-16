import typer
from typing import Optional, List
from reel import __app_name__, __version__
from reel.gitlab_api import get_last_n_jobs, save_jobs
from reel.jira_api import get_issues

import pyperclip

app = typer.Typer()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f'{__app_name__} v{__version__}')
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        '--version',
        '-v',
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return


@app.command()
def save_jobs_report(
    name: str = typer.Argument(
        'Selenium tests',
        help='The name of the jobs to save',
    ),
    status: str = typer.Option(
        None,
        '--status',
        '-s',
        help='The status of the jobs to save',
    ),
    output_file: str = typer.Option(
        'reports/gitlab_jobs_report.json',
        '--output',
        '-o',
        help='The output file to save the jobs to',
    ),
    n: int = typer.Option(
        50,
        '--n',
        '-n',
        help='The number of jobs to save',
    ),
) -> None:
    """
    Save the failed jobs to a file
    """
    jobs = get_last_n_jobs(status=status, name=name, n=n)
    save_jobs(jobs, output_file)
    return


@app.command()
def how_many_failed(
    name: str = typer.Argument(
        'Selenium tests',
        help='The name of the jobs to count',
    ),
    n: int = typer.Option(
        50,
        '--n',
        '-n',
        help='The number of jobs to count',
    ),
) -> None:
    """
    Count the number of failed jobs
    """
    jobs = get_last_n_jobs(name=name, n=n)
    failed_jobs = [job for job in jobs if job['status'] == 'failed']
    typer.echo(f'{len(failed_jobs)} failed jobs out of {n}')


@app.command()
def average_run_time(
    name: str = typer.Argument(
        'Selenium tests',
        help='The name of the jobs to count',
    ),
    n: int = typer.Option(
        50,
        '--n',
        '-n',
        help='The number of jobs to count',
    ),
) -> None:
    """
    Count the average run time of specified jobs
    """
    jobs = get_last_n_jobs(name=name, n=n)
    run_times = [int(job['duration']) for job in jobs if job['duration'] is not None]
    typer.echo(f'{sum(run_times) / len(run_times)} seconds')
    typer.echo(f"(That's {sum(run_times) / len(run_times) / 60} minutes)")


@app.command()
def issues_in_sprint(
    sprint_id: str = typer.Argument(
        '0000',
        help='The name of the jobs to count',
    ),
) -> None:
    """
    Count the number of issues in the sprint
    """
    response = get_issues(sprint_id)
    issue_list: List[str] = []
    for issue in response['issues']:
        issue_list.append(f'https://industrydive.atlassian.net/browse/{issue["key"]}')
    if len(issue_list) > 0:
        pyperclip.copy('\n'.join(issue_list))
