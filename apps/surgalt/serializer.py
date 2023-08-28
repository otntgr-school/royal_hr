from rest_framework import serializers

from core.models import Surgalt


class SurgaltPaginationSerializer(serializers.ModelSerializer):

    for_type_name = serializers.SerializerMethodField()
    for_type_value = serializers.CharField(source="for_type")

    class Meta:
        model = Surgalt
        fields = (
            "id",
            "name",
            "purpose",
            "for_type",
            "for_count",
            "start_date",
            "end_date",
            "end_time",
            "start_time",
            "employees",
            "for_type_value",
            'for_type_name'
        )

    def get_for_type_name(self, obj):
        return obj.for_type_name


class SurgaltSerializer(serializers.ModelSerializer):


    class Meta:
        model = Surgalt
        fields = '__all__'
