import os
from github import Github
import sys

from . import Service


class GitHubService(Service):
    name = "github"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            print("GITHUB_TOKEN environment variable must be set.")
            sys.exit(1)

        self.client = Github(token, per_page=100)

    def read_tasks(self, *args, **kwargs):
        user = self.client.get_user()

        print("Gathering user repositories information...")
        repos = list(user.get_repos())
        archived_repos = set(r.full_name for r in repos if r.archived)
        print("Gathering user issues across all repositories and organizations...")
        user_issues = list(user.get_user_issues(filter="all", state="all"))
        print("Gathering public issues created by user...")
        created_issues = list(self.client.search_issues(query="author:pawamoy type:all archived:false"))
        print("Gathering public issues assigned to user...")
        assigned_issues = list(self.client.search_issues(query="assignee:pawamoy type:all archived:false"))

        print("Building the unique set of issues...")
        seen = set()
        issues = []
        all_issues = user_issues + created_issues + assigned_issues
        for issue in all_issues:
            repository_url = issue._rawData["repository_url"]
            repository_full_name = "/".join(repository_url.split("/")[-2:])
            issue._rawData["repository_full_name"] = repository_full_name
            ref = repository_url + "#" + str(issue._rawData["number"])
            if ref not in seen:
                seen.add(ref)
                if repository_full_name not in archived_repos:
                    issues.append(issue)

        del all_issues
        del user_issues
        del created_issues
        del assigned_issues

        print("Transforming issues into tasks...")
        issues = [self.to_generic_task(i) for i in issues]
        return issues

    def to_generic_task(self, service_task):
        project = "git." + service_task._rawData["repository_full_name"].lower().replace(".", "-").replace("/", ".")
        # labels=[l['name'] for l in issue._rawData['labels']]
        # tags=''
        # if labels:
        #     tags='+' + ' +'.join(labels)

        entry = service_task._rawData["created_at"].replace("-", "").replace(":", "")
        end = service_task._rawData["closed_at"]
        if end:
            end = end.replace("-", "").replace(":", "")

        tw_issue = dict(
            # depends
            description="(GH) " + service_task._rawData["title"].strip(),
            # due
            end=end,
            entry=entry,
            # id
            # imask
            # mask
            # modified
            # parent
            # priority
            project=project,
            # recur
            # scheduled
            # start
            # status
            # tags=tags,
            # until
            # urgency
            # uuid
            # wait
            githuburl=service_task._rawData["html_url"],
        )

        if not tw_issue["end"]:
            del tw_issue["end"]

        return tw_issue
