from rest_framework import serializers


class UserBoxSerializer(serializers.Serializer):
    box_name = serializers.CharField(max_length=30)
    is_shown = serializers.BooleanField()
