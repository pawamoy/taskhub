import uuid

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxValueValidator

from colorful.fields import RGBColorField


class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(verbose_name=_("Title"), max_length=255)
    description = models.TextField(verbose_name=_("Description"), blank=True)

    priority = models.PositiveSmallIntegerField(
        verbose_name=_("Priority"),
        validators=[MaxValueValidator(99, _("Priority cannot be more than 99"), default=50, blank=True)],
    )

    confidential = models.BooleanField(
        verbose_name=_("Confidential"),
        help_text=_("Mark a task as confidential to easily exclude it from reports and exports."),
        default=False, blank=True)

    creation_date = models.DateTimeField(verbose_name=_("Creation date"), blank=True)
    completion_date = models.DateTimeField(verbose_name=_("Completion date"), blank=True)
    last_update = models.DateTimeField(verbose_name=_("Last update"), blank=True)
    # other events? as a JSON array?

    # status is flexible: we'll be able to draw columns
    status = models.CharField(verbose_name=_("Status"), max_length=255)

    manual_order = models.PositiveSmallIntegerField(
        verbose_name=_("Manual order"),
        help_text=_("The manual order of tasks, used to order the tasks in status columns."),
        default=0, blank=True)

    # dates
    start_date = models.DateTimeField(
        verbose_name=_("Start date"), help_text=_("The date at which the task starts."), blank=True, null=True
    )

    min_duration = models.DurationField(
        verbose_name=_("Minimum duration"),
        help_text=_("The minimum duration of the task, used to verify the validity of a given start/due date."),
        blank=True,
        null=True,
    )

    max_duration = models.DurationField(
        verbose_name=_("Maximum duration"),
        help_text=_("The maximum duration of the task, used to verify the validity of a given start/due date.."),
        blank=True,
        null=True,
    )

    due_date = models.DateTimeField(
        verbose_name=_("Due date"), help_text=_("The date at which the task is due."), blank=True, null=True
    )

    expiration_date = models.DateTimeField(
        verbose_name=_("Expiration date"),
        help_text=_("The date at which the task expires and is closed."),
        blank=True,
        null=True,
    )

    wait_date = models.DateTimeField(
        verbose_name=_("Wait date"), help_text=_("The date to wait for before showing the task."), blank=True, null=True
    )

    scheduled = models.DateTimeField(
        verbose_name=_("Scheduled date"),
        help_text=_("The date after which a task can be completed."),
        blank=True,
        null=True,
    )

    # see taskwarrior issues for types of recurrence
    # recurrence

    extra = JSONField(verbose_name=_("Extra"))


class TaskRef(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    ref = models.CharField(verbose_name=_("Reference hash"), max_length=32, unique=True)


class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(verbose_name=_("Title"), max_length=255)
    description = models.TextField(verbose_name=_("Description"))


class Rel(models.Model):
    title = models.CharField(verbose_name=_("Title"), max_length=255)
    description = models.TextField(verbose_name=_("Description"))


class TaskRel(models.Model):
    task1 = models.ForeignKey(Task, on_delete=models.CASCADE)
    task2 = models.ForeignKey(Task, on_delete=models.CASCADE)

    rel = models.ForeignKey(Rel, on_delete=models.CASCADE)


class TaskGroupRel(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)


class GroupRel(models.Model):
    group1 = models.ForeignKey(Group, on_delete=models.CASCADE)
    group2 = models.ForeignKey(Group, on_delete=models.CASCADE)


class TaskGrouping(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField()


class GroupGrouping(models.Model):
    group1 = models.ForeignKey(Group, on_delete=models.CASCADE)
    group2 = models.ForeignKey(Group, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField()


class Label(models.Model):
    title = models.CharField(verbose_name=_("Title"), max_length=255)
    description = models.TextField(verbose_name=_("Description"))
    color = RGBColorField()


class TaskLabel(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    label = models.ForeignKey(Label, on_delete=models.CASCADE)


class GroupLabel(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    label = models.ForeignKey(Label, on_delete=models.CASCADE)
