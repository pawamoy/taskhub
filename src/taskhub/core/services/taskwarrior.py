import html
from datetime import datetime

from taskw import TaskWarrior

from . import Service
from ..models import Group, GroupGrouping, Task, TaskGrouping


class TaskWarriorService(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = TaskWarrior()

    def to_generic_task(self, service_task):
        def str_to_date(d):
            return datetime(
                year=int(d[:4]),
                month=int(d[4:6]),
                day=int(d[6:8]),
                hour=int(d[9:11]),
                minute=int(d[11:13]),
                second=int(d[13:15]),
            )

        creation_date = str_to_date(service_task["entry"])

        last_updated = None
        if "modified" in service_task:
            last_updated = str_to_date(service_task["modified"])

        completion_date = None
        if "end" in service_task:
            completion_date = str_to_date(service_task["end"])

        title_description = service_task["description"].split("\n", 1)
        if len(title_description) > 1:
            title, description = title_description
        else:
            title = title_description[0]
            description = ""

        status = service_task["status"]
        uuid = service_task["uuid"]

        groups = {}
        group = None
        if "project" in service_task:
            previous_group = None
            for group in service_task["project"].split("."):
                if group not in groups:
                    groups[group] = Group(title="Project " + group)
                if previous_group:
                    GroupGrouping(group=groups[group], in_group=previous_group, order=1)
                previous_group = groups[group]

        task = Task(
            id=uuid,
            status=status,
            title=title,
            description=description,
            completion_date=completion_date,
            creation_date=creation_date,
            last_update=last_updated,
        )
        if group:
            TaskGrouping(task=task, group=groups[group], order=1)

    def to_service_task(self, generic_task):
        project = "git." + generic_task._rawData["repository_full_name"].lower().replace(".", "-").replace("/", ".")
        # labels=[l['name'] for l in issue._rawData['labels']]
        # tags=''
        # if labels:
        #     tags='+' + ' +'.join(labels)

        entry = generic_task._rawData["created_at"].replace("-", "").replace(":", "")
        end = generic_task._rawData["closed_at"]
        if end:
            end = end.replace("-", "").replace(":", "")

        tw_issue = dict(
            # depends
            description="(GH) " + generic_task._rawData["title"].strip(),
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
            githuburl=generic_task._rawData["html_url"],
        )

        return tw_issue

    def fix_tw_encoding(self, string):
        return html.unescape(
            string.replace("&dquot;", "&quot;").replace("&open;", "&lbrack;").replace("&close;", "&rbrack;")
        )

    def changed(self, new_task, old_task):
        reduced_task = {key: old_task[key] for key in new_task.keys() if key in old_task}

        reduced_task["description"] = self.fix_tw_encoding(reduced_task["description"])

        if reduced_task != new_task:
            return True
        return False

    def map_tasks(self, new_tasks, old_tasks):
        mapping = dict(matched=[], new=[], kept=[])

        def has_key(x):
            return "githuburl" in x

        def key(x):
            return x["githuburl"]

        candidates = []
        for task in old_tasks:
            if has_key(task):
                candidates.append(task)
            else:
                mapping["kept"].append(task)

        sorted_tasks = sorted(candidates, key=key)
        sorted_issues = sorted(new_tasks, key=key)

        for issue in sorted_issues:
            if not sorted_tasks:
                mapping["new"].append(issue)
                continue
            issue_key = key(issue)
            for t, task in enumerate(sorted_tasks):
                task_key = key(task)
                if issue_key == task_key:
                    mapping["matched"].append((issue, task))
                    del sorted_tasks[t]
                    break
                elif issue_key < task_key:
                    mapping["new"].append(issue)

        mapping["unmatched"] = sorted_tasks
        return mapping

    def write_tasks(self, tasks, *args, **kwargs):
        print("Loading taskwarrior tasks...")
        tw_tasks = self.client.load_tasks()
        tw_tasks = tw_tasks["pending"] + tw_tasks["completed"]

        untouched_count = 0
        updated_count = 0
        created_count = 0
        closed_count = 0
        logged_count = 0

        print("Mapping issues to existing tasks...")
        mapping = self.map_tasks(tasks, tw_tasks)

        print("All done. Starting to apply changes!")
        print("")

        print("")
        print("Updating tasks")
        print("--------------")
        print("")

        for issue, task in mapping["matched"]:
            if self.changed(issue, task):
                task.update(issue)
                _, task = self.client.task_update(task)
                if "end" in task and task["end"] and task["status"] == "pending":
                    self.client.task_done(uuid=task["uuid"])
                    closed_count += 1
                    print("Closed task {}".format(task))
                else:
                    updated_count += 1
                    print("Updated task {}".format(task))
            else:
                untouched_count += 1

        print("")
        print("Adding tasks")
        print("------------")
        print("")

        for task in mapping["new"]:
            task = self.client.task_add(**task)
            if "end" in task and task["end"]:
                self.client.task_done(uuid=task["uuid"])
                logged_count += 1
                print("Logged task {}".format(task))
            else:
                created_count += 1
                print("Created task {}".format(task))

        print("")
        print("Deleting tasks")
        print("--------------")
        print("")

        deleted_count = len(mapping["unmatched"])
        kept_count = len(mapping["kept"])

        for task in mapping["unmatched"]:
            self.client.task_delete(uuid=task["uuid"])
            print("Deleted task {}".format(task))

        print("")
        print("Summary")
        print("-------")
        print("Created     {} tasks".format(created_count))
        print("Closed      {} tasks".format(closed_count))
        print("Deleted     {} tasks".format(deleted_count))
        print("Kept        {} tasks".format(kept_count))
        print("Logged      {} tasks".format(logged_count))
        print("Updated     {} tasks".format(updated_count))
        print("Unmodified  {} tasks".format(untouched_count))
