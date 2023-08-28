from django.urls import reverse
from rest_framework import serializers

from core.models import Attachments, FeedbackKind
from core.models import Feedback

from main.utils.file import get_extension
from main.utils.file import get_name_from_path
from main.utils.file import calc_size
from main.utils.file import get_content_type
from main.utils.file import get_attachment_url
from main.utils.file import get_file_field_exists


class FeedbackKindFormSerializer(serializers.ModelSerializer):

    class Meta:
        model = FeedbackKind
        fields = "__all__"

        read_only_fields = (
            'org',
            'sub_org',
            'salbar',
        )

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data.update(request.exactly_org_filter)

        return super().create(validated_data)


class FeedbackKindListSerializer(serializers.ModelSerializer):

    text = serializers.CharField(source="title", default="")
    type = serializers.IntegerField(source="id")
    a_attr = serializers.SerializerMethodField()

    class Meta:
        model = FeedbackKind
        fields = "type", "id", 'text', 'a_attr'

    def get_a_attr(self, obj):
        return {
            "href": reverse("sanal-gomdol-turul", args=(obj.id,))
        }


class FeedbackDTSerializer(serializers.ModelSerializer):

    kind_name = serializers.SerializerMethodField()
    state_name = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = "kind_name", 'state_name', 'id', 'title', 'decided_at', 'created_at'

    def get_kind_name(self, obj):
        return obj.kind_name

    def get_state_name(self, obj):
        return obj.state_name


class AttachmentsFormSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attachments
        fields = "__all__"


class FeedbackFormSerializer(serializers.ModelSerializer):

    attachments = serializers.PrimaryKeyRelatedField(allow_empty=True, many=True, queryset=Attachments.objects.all())

    kind_name = serializers.CharField(source="kind.title", default="", read_only=True)
    state_name = serializers.CharField(source="get_state_display", default="", read_only=True)

    class Meta:
        model = Feedback
        fields = "__all__"


class AttachmentsDisplaySerializer(serializers.ModelSerializer):

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


class FeedBackDecideListSerializer(serializers.ModelSerializer):

    from_employee_name = serializers.CharField(source="from_employee.user.info.full_name", default="")
    from_employee_position = serializers.CharField(source="from_employee.org_position.name", default="")
    from_employee_img = serializers.SerializerMethodField()
    kind_name = serializers.CharField(source="kind.title", default="")
    decided_employee_name = serializers.CharField(source="decided_employee.user.info.full_name", default="")
    created_at = serializers.DateTimeField(format=("%Y-%m-%d %H:%M:%S"))
    decided_at = serializers.DateTimeField(format=("%Y-%m-%d %H:%M:%S"))

    class Meta:
        model = Feedback
        fields = "from_employee_name", "id", 'title', 'decided_at', \
            'created_at', 'from_employee_position', 'from_employee_name', 'kind_name', \
            'decided_employee_name', 'state', 'from_employee_img'

    def get_from_employee_img(self, obj):
        return obj.from_employee.real_photo.url if obj.from_employee.real_photo else None


class FeedbackUPDATESerializer(serializers.ModelSerializer):

    class Meta:
        model = Feedback
        fields = "id", 'decided_content', 'decided_at', 'state', 'decided_employee'


class FeedBackDecideGETSerializer(serializers.ModelSerializer):

    from_employee_name = serializers.CharField(source="from_employee.user.info.full_name", default="")
    from_employee_position = serializers.CharField(source="from_employee.org_position.name", default="")
    kind_name = serializers.CharField(source="kind.title", default="")
    decided_employee_name = serializers.CharField(source="decided_employee.user.info.full_name", default="")

    from_employee_org_name = serializers.CharField(source="from_employee.org.name", default="")
    from_employee_sub_org_name = serializers.CharField(source="from_employee.sub_org.name", default="")
    from_employee_salbar_name = serializers.CharField(source="from_employee.salbar.name", default="")

    created_at = serializers.DateTimeField(format=("%Y-%m-%d %H:%M:%S"))
    decided_at = serializers.DateTimeField(format=("%Y-%m-%d %H:%M:%S"))
    attachments = AttachmentsDisplaySerializer(many=True)
    commands = AttachmentsDisplaySerializer(many=True)
    state_name = serializers.CharField(source="get_state_display")
    user_id = serializers.CharField(source="from_employee.user.id", default="")

    class Meta:
        model = Feedback
        fields = "__all__"


class FeedbackGETSerializer(serializers.ModelSerializer):

    attachments = AttachmentsDisplaySerializer(many=True)
    state_name = serializers.CharField(source="get_state_display")
    org_name = serializers.CharField(source="org.name", default="")
    sub_org_name = serializers.CharField(source="sub_org.name", default="")
    salbar_name = serializers.CharField(source="salbar.name", default="")
    employee_name = serializers.CharField(source="to_employees.full_name", default="")

    class Meta:
        model = Feedback
        fields = "__all__"


class FeedbackGETAttachSerializer(serializers.ModelSerializer):

    attachments = AttachmentsDisplaySerializer(many=True)

    class Meta:
        model = Feedback
        fields = ("attachments",)


class FeedbackGETCommandshSerializer(serializers.ModelSerializer):

    attachments = AttachmentsDisplaySerializer(source="commands", many=True)

    class Meta:
        model = Feedback
        fields = ("attachments",)
