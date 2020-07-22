from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Group, GroupGrouping, GroupRel, Label, Rel, Task, TaskGrouping, TaskGroupRel, TaskRef, TaskRel


class TasksInGroupInline(admin.TabularInline):
    model = Group.tasks.through
    extra = 0
    verbose_name = _("Task")
    verbose_name_plural = _("Tasks in this group")


class GroupsContainingTaskInline(admin.TabularInline):
    model = Group.tasks.through
    extra = 0
    verbose_name = _("Group")
    verbose_name_plural = _("Groups containing this task")


class GroupsContainingGroupInline(admin.TabularInline):
    model = Group.groups.through
    fk_name = "group"
    extra = 0
    verbose_name = _("Group")
    verbose_name_plural = _("Groups containing this group")


class GroupsContainedByGroupInline(admin.TabularInline):
    model = Group.groups.through
    fk_name = "in_group"
    extra = 0
    verbose_name = _("Group")
    verbose_name_plural = _("Groups contained by this group")


class GroupLabelsInline(admin.TabularInline):
    model = Group.labels.through
    extra = 0
    verbose_name = _("Label")
    verbose_name_plural = _("Group's labels")


class TaskLabelsInline(admin.TabularInline):
    model = Task.labels.through
    extra = 0
    verbose_name = _("Label")
    verbose_name_plural = _("Task's labels")


class LabelGroupsInline(admin.TabularInline):
    model = Group.labels.through
    extra = 0
    verbose_name = _("Group")
    verbose_name_plural = _("Groups with this label")


class LabelTasksInline(admin.TabularInline):
    model = Task.labels.through
    extra = 0
    verbose_name = _("Task")
    verbose_name_plural = _("Tasks with this label")


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    inlines = (TasksInGroupInline, GroupsContainedByGroupInline, GroupsContainingGroupInline)
    list_display = ("id", "title", "description")


@admin.register(GroupGrouping)
class GroupGroupingAdmin(admin.ModelAdmin):
    list_display = ("group", "in_group", "order")


@admin.register(GroupRel)
class GroupRelAdmin(admin.ModelAdmin):
    list_display = ("from_group", "rel", "to_group")


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    inlines = (LabelTasksInline, LabelGroupsInline)
    list_display = ("title", "description", "color")


@admin.register(Rel)
class RelAdmin(admin.ModelAdmin):
    list_display = ("title", "description")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    inlines = (GroupsContainingTaskInline, TaskLabelsInline)
    list_display = (
        "id",
        "title",
        "status",
        "creation_date",
        "completion_date",
        "last_update",
        "priority",
        "confidential",
    )


@admin.register(TaskGrouping)
class TaskGroupingAdmin(admin.ModelAdmin):
    list_display = ("task", "group", "order")


@admin.register(TaskGroupRel)
class TaskGroupRelAdmin(admin.ModelAdmin):
    list_display = ("task", "rel", "group")


@admin.register(TaskRef)
class TaskRefAdmin(admin.ModelAdmin):
    list_display = ("task", "ref")


@admin.register(TaskRel)
class TaskRelAdmin(admin.ModelAdmin):
    list_display = ("task1", "rel", "task2")
