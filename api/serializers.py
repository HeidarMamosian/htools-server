from rest_framework import serializers


class PageSerializer(serializers.Serializer):
    url = serializers.CharField(allow_blank=True, allow_null=True)
    text = serializers.CharField(allow_blank=True, allow_null=True)
    status = serializers.IntegerField()
    links = serializers.ListField(
        child=serializers.CharField(allow_blank=True, allow_null=True)
    )
