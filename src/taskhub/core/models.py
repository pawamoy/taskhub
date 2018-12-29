import uuid

from colorful.fields import RGBColorField
from django.contrib.postgres.fields import JSONField
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

QTaskOrGroup = Q(app_label="core", model="task") | Q(app_label="core", model="group")


class Label(models.Model):
    title = models.CharField(verbose_name=_("Title"), max_length=255)
    description = models.TextField(verbose_name=_("Description"))
    color = RGBColorField()

    class Meta:
        verbose_name = _("Label")
        verbose_name_plural = _("Labels")

    def __str__(self):
        return self.title


class Rel(models.Model):
    title = models.CharField(verbose_name=_("Title"), max_length=255)
    description = models.TextField(verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Relationship")
        verbose_name_plural = _("Relationships")

    def __str__(self):
        return self.title


class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(verbose_name=_("Title"), max_length=255)
    description = models.TextField(verbose_name=_("Description"), blank=True)

    priority = models.PositiveSmallIntegerField(
        verbose_name=_("Priority"),
        validators=[MaxValueValidator(99, _("Priority cannot be more than 99"))],
        default=50,
        blank=True,
    )

    confidential = models.BooleanField(
        verbose_name=_("Confidential"),
        help_text=_("Mark a task as confidential to easily exclude it from reports and exports."),
        default=False,
        blank=True,
    )

    labels = models.ManyToManyField(Label)

    creation_date = models.DateTimeField(verbose_name=_("Creation date"), blank=True, null=True)
    completion_date = models.DateTimeField(verbose_name=_("Completion date"), blank=True, null=True)
    last_update = models.DateTimeField(verbose_name=_("Last update"), blank=True, null=True)
    # other events? as a JSON array?

    # status is flexible: we'll be able to draw columns
    status = models.CharField(verbose_name=_("Status"), max_length=255)

    manual_order = models.PositiveSmallIntegerField(
        verbose_name=_("Manual order"),
        help_text=_("The manual order of tasks, used to order the tasks in status columns."),
        default=0,
        blank=True,
    )

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

    extra = JSONField(verbose_name=_("Extra"), blank=True, null=True)

    # related_tasks = GenericRelation(
    #     Relationships,
    #     content_type_field='content_type_fk',
    #     object_id_field='object_primary_key'
    # )
    # related_groups = GenericRelation(
    #     Relationships,
    #     content_type_field='content_type_fk',
    #     object_id_field='object_primary_key'
    # )

    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")

    def __str__(self):
        return self.title


class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(verbose_name=_("Title"), max_length=255)
    description = models.TextField(verbose_name=_("Description"))

    labels = models.ManyToManyField(Label)

    tasks = models.ManyToManyField(Task, through="TaskGrouping", through_fields=("group", "task"))
    groups = models.ManyToManyField("Group", through="GroupGrouping", through_fields=("in_group", "group"))

    class Meta:
        verbose_name = _("Group")
        verbose_name_plural = _("Groups")

    def __str__(self):
        return self.title


class TaskRef(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    ref = models.CharField(verbose_name=_("Reference hash"), max_length=32, unique=True)

    class Meta:
        verbose_name = _("Task reference")
        verbose_name_plural = _("Task references")

    def __str__(self):
        return f"{self.task}: {self.ref}"


class TaskRel(models.Model):
    task1 = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="task_rels_1")
    task2 = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="task_rels_2")

    rel = models.ForeignKey(Rel, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Relationship between two tasks")
        verbose_name_plural = _("Relationships between tasks")

    def __str__(self):
        return f"{self.task1} - {self.rel} - {self.task2}"


class TaskGroupRel(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    rel = models.ForeignKey(Rel, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Relationship between a task and a group")
        verbose_name_plural = _("Relationships between tasks and groups")

    def __str__(self):
        return f"{self.task} - {self.rel} - {self.group}"


class GroupRel(models.Model):
    from_group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="from_group_rels")
    to_group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="to_group_rels")

    rel = models.ForeignKey(Rel, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Relationship between two groups")
        verbose_name_plural = _("Relationships between groups")

    def __str__(self):
        return f"{self.from_group} - {self.rel} - {self.to_group}"


class TaskGrouping(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="in_groups")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="has_tasks")
    order = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = _("Task in Group")
        verbose_name_plural = _("Tasks in Groups")
        unique_together = ("task", "group")

    def __str__(self):
        return f"{self.task} is in {self.group} at pos. {self.order}"


class GroupGrouping(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="in_groups")
    in_group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="has_groups")
    order = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = _("Group in Group")
        verbose_name_plural = _("Groups in Groups")
        unique_together = ("group", "in_group")

    def __str__(self):
        return f"{self.group} is in {self.in_group} at pos. {self.order}"
