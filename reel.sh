#!/bin/sh
CWD = pwd
cd ~/Development/jira-to-gitlab/
pipenv run python -m reel $@
cd $CWD
