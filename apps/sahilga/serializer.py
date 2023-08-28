from rest_framework import serializers
from feedback.serializer import AttachmentsDisplaySerializer

from core.models import Sahilga


class SahilgaActionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sahilga
        fields = "__all__"


class EmployeeSahilgaSerializer(serializers.ModelSerializer):

    start_date = serializers.DateField(format=("%Y-%m-%d"))

    class Meta:
        model = Sahilga
        fields = "__all__"


class SahilgaGETSerializer(serializers.ModelSerializer):

    attachments = AttachmentsDisplaySerializer(many=True)

    class Meta:
        model = Sahilga
        fields = "__all__"


class SahilgaReadOneEmpSerializer(serializers.ModelSerializer):
    state = serializers.CharField(source="get_state_display")

    class Meta:
        model = Sahilga
        fields = "__all__"
