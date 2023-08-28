from django.db.models.functions import Trunc
from django.db import models

from rest_framework import serializers

from core.models import (
    Employee,
    ShagnalEmployee,
    StaticShagnal,
    Shagnal
)


class StaticShagnalFormSerializer(serializers.ModelSerializer):

    class Meta:
        model = StaticShagnal
        fields = "name", 'id'


class DynamicShagnalFormSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shagnal
        fields = "name", 'id'

    def create(self, validated_data):
        request = self.context.get("request")
        filters = self.context.get("filters")
        validated_data.update(filters)
        validated_data['created_by'] = request.employee
        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        filters = self.context.get("filters")
        validated_data.update(filters)
        instance = super().update(instance, validated_data)
        return instance


class ShagnalEmployeeFormSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShagnalEmployee
        fields = "__all__"


class YearsEmployeeListDetailSerializer(serializers.ModelSerializer):

    user_detail = serializers.SerializerMethodField()

    class Meta:
        model = ShagnalEmployee
        fields = '__all__'

    def get_user_detail(self, obj):
        info = (
            obj.employee.user.info
            if obj.kind == ShagnalEmployee.KIND_DYNAMIC
            else
            obj.user.info
        )
        return {
            "first_name": info.first_name,
            "last_name": info.last_name,
        }


class ShagnalEmployeeListSerializer(serializers.ModelSerializer):

    years = serializers.SerializerMethodField()
    kind = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Shagnal
        fields = "__all__"

    def get_kind(self, obj):
        return obj.kind

    def get_years(self, obj):
        years = obj \
                    .shagnalemployee_set \
                    .annotate(
                        year=Trunc('what_year', 'year', output_field=models.DateTimeField())
                    ) \
                    .values('year') \
                    .annotate(count=models.Count("year")) \
                    .order_by("-year")

        data = list()
        for year in years:
            qs = obj.shagnalemployee_set.filter(what_year__year=year['year'].year)
            data.append(
                {
                    "year": year,
                    "employees": YearsEmployeeListDetailSerializer(qs, many=True, default=[]).data
                }
            )

        return data


class ShagnalTailanSerializer(serializers.ModelSerializer):

    employee_name = serializers.SerializerMethodField()
    employee_state = serializers.SerializerMethodField()

    class Meta:
        model = ShagnalEmployee
        fields = (
            '__all__'
        )

    def get_employee_state(self, obj):
        return (
            obj.employee.state
            if obj.kind == ShagnalEmployee.KIND_DYNAMIC
            else
            obj.user.employee.state
        )

    def get_employee_name(self, obj):
        return (
            obj.employee.full_name
            if obj.kind == ShagnalEmployee.KIND_DYNAMIC
            else
            obj.user.full_name
        )
