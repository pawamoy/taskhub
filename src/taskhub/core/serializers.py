from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Task, Label, Group


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "is_staff"]


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ["id", "description", "color"]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "title", "description", "priority", "confidential"]


class GroupSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ["id", "title", "description", "labels", "tasks"]

    # def create(self, validated_data):
    #     labels_data = validated_data.pop("labels")
    #     tasks_data = validated_data.pop("tasks")

