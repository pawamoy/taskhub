#!/usr/bin/env python

import os
import html
from github import Github
from taskw import TaskWarrior
import sys

token = os.environ.get('GITHUB_TOKEN')
if not token:
    print("GITHUB_TOKEN environment variable must be set.")
    sys.exit(1)

g = Github(, per_page=100)
tw = TaskWarrior()

user = g.get_user()


print('Gathering user repositories information...')
repos = list(user.get_repos())
archived_repos = set(r.full_name for r in repos if r.archived)
print('Gathering user issues across all repositories and organizations...')
user_issues = list(user.get_user_issues(filter='all', state='all'))
print('Gathering public issues created by user...')
created_issues = list(g.search_issues(query='author:pawamoy type:all archived:false'))
print('Gathering public issues assigned to user...')
assigned_issues = list(g.search_issues(query='assignee:pawamoy type:all archived:false'))

print('Building the unique set of issues...')
seen = set()
issues = []
all_issues = user_issues + created_issues + assigned_issues
for issue in all_issues:
    repository_url = issue._rawData['repository_url']
    repository_full_name = '/'.join(repository_url.split('/')[-2:])
    issue._rawData['repository_full_name'] = repository_full_name
    ref = repository_url + '#' + str(issue._rawData['number'])
    if ref not in seen:
        seen.add(ref)
        if repository_full_name not in archived_repos:
            issues.append(issue)

del all_issues
del user_issues
del created_issues
del assigned_issues


def github_to_taskwarrior(issue):
    project='git.' + issue._rawData['repository_full_name'].lower().replace('.', '-').replace('/', '.')
    # labels=[l['name'] for l in issue._rawData['labels']]
    # tags=''
    # if labels:
    #     tags='+' + ' +'.join(labels)

    entry = issue._rawData['created_at'].replace('-', '').replace(':', '')
    end = issue._rawData['closed_at']
    if end:
        end = end.replace('-', '').replace(':', '')

    tw_issue = dict(
        # depends
        description='(GH) ' + issue._rawData['title'].strip(),
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

        githuburl=issue._rawData['html_url'],
    )

    if not tw_issue['end']:
        del tw_issue['end']

    return tw_issue


print('Transforming issues into tasks...')
issues = [github_to_taskwarrior(i) for i in issues]

print('Loading taskwarrior tasks...')
tw_tasks = tw.load_tasks()
tw_tasks = tw_tasks['pending'] + tw_tasks['completed']


def fix_tw_encoding(s):
    return html.unescape(
        s
        .replace('&dquot;', '&quot;')
        .replace('&open;', '&lbrack;')
        .replace('&close;', '&rbrack;')
    )


def changed(issue, task):
    reduced_task = {
        key: task[key] for key in issue.keys() if key in task
    }

    reduced_task['description'] = fix_tw_encoding(reduced_task['description'])

    if reduced_task != issue:
        return True
    return False


def map_issues_to_tasks(issues, tasks):
    mapping = dict(
        matched=[],
        new=[],
        kept=[]
    )

    def has_key(x):
        return 'githuburl' in x

    def key(x):
        return x['githuburl']

    candidates = []
    for task in tasks:
        if has_key(task):
            candidates.append(task)
        else:
            mapping['kept'].append(task)

    sorted_tasks = sorted(candidates, key=key)
    sorted_issues = sorted(issues, key=key)

    for issue in sorted_issues:
        if not sorted_tasks:
            mapping['new'].append(issue)
            continue
        issue_key = key(issue)
        for t, task in enumerate(sorted_tasks):
            task_key = key(task)
            if issue_key == task_key:
                mapping['matched'].append((issue, task))
                del sorted_tasks[t]
                break
            elif issue_key < task_key:
                mapping['new'].append(issue)

    mapping['unmatched'] = sorted_tasks
    return mapping


untouched_count = 0
updated_count = 0
created_count = 0
closed_count = 0
logged_count = 0

print('Mapping issues to existing tasks...')
mapping = map_issues_to_tasks(issues, tw_tasks)

print('All done. Starting to apply changes!')
print('')

print('')
print('Updating tasks')
print('--------------')
print('')

for issue, task in mapping['matched']:
    if changed(issue, task):
        task.update(issue)
        _, task = tw.task_update(task)
        if 'end' in task and task['end'] and task['status'] == 'pending':
            tw.task_done(uuid=task['uuid'])
            closed_count += 1
            print('Closed task {}'.format(task))
        else:
            updated_count += 1
            print('Updated task {}'.format(task))
    else:
        untouched_count += 1

print('')
print('Adding tasks')
print('------------')
print('')

for task in mapping['new']:
    task = tw.task_add(**task)
    if 'end' in task and task['end']:
        tw.task_done(uuid=task['uuid'])
        logged_count += 1
        print('Logged task {}'.format(task))
    else:
        created_count += 1
        print('Created task {}'.format(task))

print('')
print('Deleting tasks')
print('--------------')
print('')

deleted_count = len(mapping['unmatched'])
kept_count = len(mapping['kept'])

for task in mapping['unmatched']:
    tw.task_delete(uuid=task['uuid'])
    print('Deleted task {}'.format(task))

print('')
print('Summary')
print('-------')
print('Created     {} tasks'.format(created_count))
print('Closed      {} tasks'.format(closed_count))
print('Deleted     {} tasks'.format(deleted_count))
print('Kept        {} tasks'.format(kept_count))
print('Logged      {} tasks'.format(logged_count))
print('Updated     {} tasks'.format(updated_count))
print('Unmodified  {} tasks'.format(untouched_count))
