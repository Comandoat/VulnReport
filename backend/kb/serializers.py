# KB Serializers - Noa
from rest_framework import serializers

from .models import KBEntry, Resource


class KBEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = KBEntry
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class KBEntryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = KBEntry
        fields = ["id", "name", "severity_default", "category", "updated_at"]
        read_only_fields = fields


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = "__all__"
        read_only_fields = ["id"]
