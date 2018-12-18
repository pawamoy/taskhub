from .github import GitHubService
from .stdio import StandardInputService, StandardOutputService
from .taskhub import TaskHubService
from .taskwarrior import TaskWarriorService

SERVICES = {
    srv.name: srv
    for srv in (GitHubService, StandardInputService, StandardOutputService, TaskHubService, TaskWarriorService)
}


class Service:
    name = None

    def __init__(self, *args, **kwargs):
        raise NotImplementedError

    def read_tasks(self, *args, **kwargs):
        raise NotImplementedError

    def to_generic_task(self, service_task):
        raise NotImplementedError

    def to_service_task(self, generic_task):
        raise NotImplementedError

    def write_tasks(self, tasks, *args, **kwargs):
        raise NotImplementedError


__all__ = [
    "GitHubService",
    "TaskWarriorService",
    "TaskHubService",
    "Service",
    "StandardOutputService",
    "StandardInputService",
    "SERVICES",
]
