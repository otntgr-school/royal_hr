from rest_framework import serializers

from core.models import Command
from core.models import Attachments
from core.models import Employee

from main.utils.file import get_extension, get_file_field_exists
from main.utils.file import get_name_from_path
from main.utils.file import calc_size
from main.utils.file import get_content_type
from main.utils.file import get_attachment_url


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachments
        fields = '__all__'


class AttachmentsDisplaySerializer(serializers.ModelSerializer):

    path = serializers.CharField(source="file.path")
    url = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    ext = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    pure_size = serializers.SerializerMethodField()
    mime_type = serializers.SerializerMethodField()
    has_file = serializers.SerializerMethodField()

    class Meta:
        model = Attachments
        fields = "__all__"

    def get_url(self, obj):
        return get_attachment_url(obj.id)

    def get_name(self, obj):
        name = obj.file.name
        return get_name_from_path(name)

    def get_ext(self, obj):
        path = obj.file.path
        return "".join(get_extension(path))

    def get_size(self, obj):
        size = obj.file.size if get_file_field_exists(obj.file) else ""
        return calc_size(size) if size else 0

    def get_pure_size(self, obj):
        return obj.file.size if get_file_field_exists(obj.file) else 0

    def get_mime_type(self, obj):
        data = get_content_type(obj.file.path)
        return data[0]

    def get_has_file(self, obj):
        return get_file_field_exists(obj.file)


class EmployeeInfoSerilaizer(serializers.ModelSerializer):
    full_name= serializers.CharField(source="user.info.full_name", read_only=True)
    register =  serializers.CharField(source="user.info.register", read_only=True)

    class Meta:
        model = Employee
        fields = (
            "id",
            "full_name",
            "register",
        )


class CommandPaginationSerializer(serializers.ModelSerializer):

    unit_name = serializers.SerializerMethodField()
    formated_created_at = serializers.SerializerMethodField()
    commander_name = serializers.CharField(source="commander.user.info.full_name")
    employee_list = EmployeeInfoSerilaizer(source="employees", many=True, read_only=True)

    class Meta:
        model = Command
        exclude = "attachments",

    def get_unit_name(self, obj):
        return obj.unit_name

    def get_formated_created_at(self, obj):
        return obj.formated_created_at


class CommandSerializer(serializers.ModelSerializer):

    class Meta:
        model = Command
        fields = '__all__'


class CommandDisplaySerializer(serializers.ModelSerializer):

    attachments = AttachmentsDisplaySerializer(many=True)

    class Meta:
        model = Command
        fields = '__all__'

class CommandAttachsSerializer(serializers.ModelSerializer):

    attachments = AttachmentsDisplaySerializer(many=True)

    class Meta:
        model = Command
        fields = ('attachments',)
