from django.urls import reverse

from rest_framework import serializers

from core.models import (
    Notification,
    NotificationState,
    NotificationType,
    SubOrgs,
    Salbars,
    OrgPosition,
    Orgs,
    User,
)


def get_query(context):
    kind = context.get("view").kwargs.get("kind")
    return kind


def need_children(context):
    """ children ийг авах хэрэгтэй эсэх """
    query = get_query(context)
    if query == Notification.SCOPE_KIND_POS:
        return False, query
    if query == Notification.SCOPE_KIND_SUBORG:
        return False, query

    return True, query


class NotificationActionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = "__all__"


class SalbarJsonSerializer(serializers.ModelSerializer):

    children = serializers.SerializerMethodField()
    text = serializers.CharField(source="name")
    type = serializers.IntegerField(source="id")
    id = serializers.SerializerMethodField()

    class Meta:
        model = Salbars
        fields = 'type', 'text', 'children', 'id'

    def get_id(self, obj):
        return f"salbar_{obj.id}"

    def get_children(self, obj):

        children = SalbarJsonSerializer(
            Salbars.objects.filter(
                parent_id=obj.id
            ),
            many=True,
        ).data

        return children


class SubOrgJsonSerializer(serializers.ModelSerializer):

    children = serializers.SerializerMethodField()
    text = serializers.CharField(source="name")
    type = serializers.IntegerField(source="id")
    id = serializers.SerializerMethodField()

    class Meta:
        model = SubOrgs
        fields = 'type', 'text', 'children', 'id'

    def get_id(self, obj):
        return f"sub_{obj.id}"

    def get_children(self, obj):
        request = self.context.get("request")
        need, query = need_children(self.context)
        if not need:
            return []

        qs = obj.salbars_set.filter(branch_pos=0)
        return SalbarJsonSerializer(qs, many=True, context={ "request": request }).data


class OrgPositionJsonSerializer(serializers.ModelSerializer):

    text = serializers.CharField(source="name")
    type = serializers.IntegerField(source="id")
    id = serializers.SerializerMethodField()

    class Meta:
        model = OrgPosition
        fields = 'type', 'text', 'id'

    def get_id(self, obj):
        return f"pos_{obj.id}"


class OrgSerializer(serializers.ModelSerializer):

    text = serializers.CharField(source="name")
    type = serializers.IntegerField(source="id")
    id = serializers.SerializerMethodField()

    class Meta:
        model = Orgs
        fields = "type", 'text', 'id'

    def get_id(self, obj):
        return f"org_{obj.id}"


class UserSerializer(serializers.ModelSerializer):

    text = serializers.SerializerMethodField()
    type = serializers.IntegerField(source="id")
    id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = "type", 'text', 'id'

    def get_id(self, obj):
        return f"user_{obj.id}"

    def get_text(self, obj):
        return obj.info.full_name() if obj.info else ""


class NotificationListSerializer(serializers.ModelSerializer):

    icon = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    lvl_color = serializers.CharField(source="ntype.color", default="")
    lvl_name = serializers.CharField(source="ntype.name", default="")

    class Meta:
        model = Notification
        fields = "__all__"

    def get_name(self, obj):
        name = None

        form_field = {
            Notification.FROM_KIND_ORG: ["from_org", "name"],
            Notification.FROM_KIND_SUBORG: ["from_sub_org", 'name'],
            Notification.FROM_KIND_SALBAR: ["from_salbar", 'name'],
            Notification.FROM_KIND_POS: ["from_org_position", 'name'],
            Notification.FROM_KIND_EMPLOYEE: ["from_employees", 'full_name'],
            Notification.FROM_KIND_USER: ["from_users", 'full_name'],
        }.get(obj.from_kind)

        if not form_field:
            return None

        from_obj = getattr(obj, form_field[0])
        if from_obj:
            name = getattr(from_obj, form_field[1])

        return name

    def get_icon(self, obj):
        icon = None

        form_field = {
            Notification.FROM_KIND_ORG: ["from_org", "logo"],
            Notification.FROM_KIND_SUBORG: ["from_sub_org", 'logo'],
            Notification.FROM_KIND_SALBAR: ["from_salbar", 'logo'],
            Notification.FROM_KIND_POS: ["from_org_position", ''],
            Notification.FROM_KIND_EMPLOYEE: ["from_employees", 'real_photo'],
            Notification.FROM_KIND_USER: ["from_users", 'real_photo'],
        }.get(obj.from_kind)

        if not form_field:
            return None

        img_field = form_field[1]

        from_obj = getattr(obj, form_field[0])
        if from_obj and img_field and hasattr(from_obj, img_field):
            icon_obj = getattr(from_obj, img_field)
            icon = icon_obj.url if icon_obj else None

        return icon


class NotifTypeFormSerializer(serializers.ModelSerializer):

    name = serializers.CharField(label="Гарчиг")
    color = serializers.CharField(style={ "input_type": "color" }, label="Илэрхийлэх өнгө")
    level = serializers.IntegerField(label="Зэрэг")

    class Meta:
        model = NotificationType
        fields = "__all__"


class NotifTypeListSerializer(serializers.ModelSerializer):

    text = serializers.CharField(source="name", default="")
    type = serializers.IntegerField(source="id")
    a_attr = serializers.SerializerMethodField()

    class Meta:
        model = NotificationType
        fields = "type", "id", 'text', 'a_attr', "color"

    def get_a_attr(self, obj):
        return {
            "href": reverse("notif-type", args=(obj.id,))
        }
