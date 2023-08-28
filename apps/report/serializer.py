import os

from rest_framework import serializers

from core.models import Employee
from core.models import Feedback
from core.models import HrOrderFormEmployee
from core.models import ViolationRegistrationPage


class ReportUrgudulDTSerializer(serializers.ModelSerializer):

    from_employee_name = serializers.SerializerMethodField()
    to_employee_name = serializers.SerializerMethodField()
    state_name = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format=("%Y-%m-%d %H:%M:%S"), read_only=True)
    decided_at = serializers.DateTimeField(format=("%Y-%m-%d %H:%M:%S"), read_only=True)
    kind_name = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = (
            "__all__"
        )

    def get_from_employee_name(self, obj):
        return obj.from_employee_name

    def get_to_employee_name(self, obj):
        return obj.to_employee_name

    def get_state_name(self, obj):
        return obj.state_name

    def get_kind_name(self, obj):
        return obj.kind_name


class HrOrderFormEmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = HrOrderFormEmployee
        fields = "__all__"


class ViolationRegistrationPageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ViolationRegistrationPage
        fields = "__all__"


class HrOrderFormEmployeeJsonSerializer(serializers.ModelSerializer):

    file_name = serializers.SerializerMethodField()
    state_name = serializers.CharField(source="get_state_display", default='')
    created_at = serializers.DateTimeField(format=("%Y-%m-%d %H:%M"), read_only=True)

    class Meta:
        model = HrOrderFormEmployee
        fields = "__all__"

    def get_file_name(self, obj):

        return os.path.basename(obj.file.name)


class EmployeeSerializer(serializers.ModelSerializer):

    salbar_name = serializers.SerializerMethodField()
    name = serializers.CharField(source='full_name', default='')

    class Meta:
        model = Employee
        fields = "__all__"

    def get_salbar_name(self, obj):

        name = ''

        if obj.salbar:
            name = obj.salbar.name
        elif obj.sub_org:
            name = obj.sub_org.name
        else:
            name = obj.org.name

        return name


class HrOrderFormEmployeeAnswerJsonSerializer(serializers.ModelSerializer):

    file_name = serializers.SerializerMethodField()
    state_name = serializers.CharField(source="get_state_display", default='')
    created_at = serializers.DateTimeField(format=("%Y-%m-%d %H:%M"), read_only=True)
    employee = EmployeeSerializer()

    class Meta:
        model = HrOrderFormEmployee
        fields = "__all__"

    def get_file_name(self, obj):
        return os.path.basename(obj.file.name)


class ViolationRegistrationPageJsonSerializer(serializers.ModelSerializer):

    file_name = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format=("%Y-%m-%d %H:%M"), read_only=True)
    employee = EmployeeSerializer()

    class Meta:
        model = ViolationRegistrationPage
        fields = "__all__"

    def get_file_name(self, obj):
        return os.path.basename(obj.file.name)
