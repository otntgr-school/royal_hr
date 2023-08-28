from rest_framework import serializers

from core.models import OrgPosition
from core.models import Roles
from core.models import Permissions
from core.models import AlbanTushaalBatalgaajuulalt
from core.models import AlbanTushaalShaardlaga
from core.models import AlbanTushaalSubject
from core.models import AlbanTushaaliinTodGeneral
from core.models import AlbanTushaaliinTodZorilgo
from core.models import AlbanTushaaliinTodorhoilolt
from core.models import AlbanTushaaliinZorilt
from core.models import AlbanTushaaliinZoriltiinVvreg
from core.models import EmployeeDonation
from core.models import Orgs
from core.models import MainPosition


class RoleSerializer(serializers.ModelSerializer):

    cname = serializers.CharField(source="name", label="Нэр", style={ "placeholder": "Нэр өгөх" })
    cdescription = serializers.CharField(source="description", label="Тайлбар", style={ "placeholder": "Тайлбар өгөх" })
    cpermissions = serializers.PrimaryKeyRelatedField(
        source="permissions",
        label="Эрхүүд",
        style={'template': "form/multi-select.html"},
        allow_empty=False,
        many=True,
        queryset=Permissions.objects.all()
    )

    class Meta:
        model = Roles
        exclude = "name", 'description', 'permissions'


class RolePaginationSerializer(serializers.ModelSerializer):
    """ Role хуудаслалт хийхэд хэрэглэгдэнэ """

    created_at = serializers.DateTimeField(format=("%Y-%m-%d %H:%M:%S"))

    class Meta:
        model = Roles
        fields = "id", 'name', 'description', 'created_at'


class PermPaginationSerializer(serializers.ModelSerializer):
    """ Эрхүүд хуудаслалт хийхэд хэрэглэгдэнэ """

    created_at = serializers.DateTimeField(format=("%Y-%m-%d %H:%M:%S"))

    class Meta:
        model = Permissions
        fields = "id", 'name', 'description', 'created_at'


class RoleActionSerializer(serializers.ModelSerializer):

    cname = serializers.CharField(source="name", label="Нэр", style={ "placeholder": "Нэр өгөх" })
    cdescription = serializers.CharField(source="description", label="Тайлбар", style={ "placeholder": "Тайлбар өгөх" })

    class Meta:
        model = Roles
        exclude = "name", 'description'


class PermissionsActionSerializer(serializers.ModelSerializer):

    cname = serializers.CharField(source="name", label="Нэр", style={ "placeholder": "Нэр өгөх" })
    cdescription = serializers.CharField(source="description", label="Тайлбар", style={ "placeholder": "Тайлбар өгөх" })
    # time = serializers.TimeField(style={"template": "form/time.html"})

    class Meta:
        model = Permissions
        exclude = "name", 'description'


class PositionExtraPermission(serializers.ModelSerializer):

    text = serializers.SerializerMethodField()
    type = serializers.IntegerField(source="id")
    icon = serializers.SerializerMethodField()

    class Meta:
        model = Permissions
        fields = "text", 'type', 'icon'

    def get_text(self, obj):
        return f"""
            <span style='font-weight: 600' title="{obj.description}">{obj.name}</span> - <span title="{obj.description}">{obj.description}</span>
        """

    def get_icon(self, obj):
        removed_perms = self.context.get('removed_perms')
        if removed_perms and obj.id in removed_perms:
            return "fas fa-times text-danger"
        return None


class RolesTreeSerializer(serializers.ModelSerializer):
    """ jstree д зориулсан role дата бэлдэх нь """

    text = serializers.CharField(source="name")
    type = serializers.IntegerField(source="id")
    children = serializers.SerializerMethodField()

    class Meta:
        model = Roles
        fields = "text", 'type', 'children'

    def get_children(self, obj):
        """ Тухайн role дээрх эрхийг харуулна хасагдсан эрхийг хасаж харуулна """

        removed_perms = self.context.get('removed_perms')
        if removed_perms:
            removed_perms = list(removed_perms.values_list('id', flat=True))
        children = PositionExtraPermission(instance=obj.permissions, many=True, context={ "removed_perms": removed_perms }).data
        return children


class PositionsTreeSerializer(serializers.ModelSerializer):
    """ Албан тушаалын мод хэлбэртэй доороо эрхүүд ийг агуулснаар авах """

    type = serializers.IntegerField(source="id")
    text = serializers.CharField(source="name")
    children = serializers.SerializerMethodField()
    a_attr = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = OrgPosition
        fields = "__all__"

    def get_children(self, obj):
        """ Role дээр нэмэлтээр сонгосон эрхүүдийг нэмж өгөх нь """

        main_children = RolesTreeSerializer(instance=obj.roles, many=True, context={ 'removed_perms': obj.removed_perms }).data
        extra_children = PositionExtraPermission(instance=obj.permissions, context={ 'removed_perms': list(obj.removed_perms.values_list('id', flat=True)) if obj.removed_perms.exists() else [] }, many=True).data

        children = main_children
        if extra_children:
            children = children +   [{
                                        "text": "Нэмэлт эрхүүд",
                                        "children": extra_children
                                    }]

        return children

    def get_a_attr(self, obj):

        return {
            "href": f"/role/position/{str(obj.id)}/"
        }


class OrgPositionSerializer(serializers.ModelSerializer):

    cname = serializers.CharField(source="name", label="Нэр")
    cmain_position = serializers.IntegerField(source="main_position.id", default=None)
    croles = serializers.PrimaryKeyRelatedField(
        source="roles",
        label="Role",
        style={'template': "form/multi-select.html"},
        allow_empty=True,
        many=True,
        queryset=Roles.objects.all()
    )
    cpermissions = serializers.PrimaryKeyRelatedField(
        source="permissions",
        label="Нэмэлт эрхүүд",
        style={'template': "form/multi-select.html"},
        allow_empty=True,
        required=False,
        many=True,
        queryset=Permissions.objects.all()
    )

    class Meta:
        model = OrgPosition
        exclude = "permissions", "name", 'roles', 'org', 'removed_perms', 'main_position'

    def create(self, validated_data):
        validated_data['org'] = self.context.get("org")

        if self.context.get("main_position"):
            main_position_qs = MainPosition.objects.get(pk=self.context.get("main_position"))
            validated_data['main_position'] = main_position_qs

        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        validated_data['org'] = self.context.get("org")

        if self.context.get("main_position"):
            main_position_qs = MainPosition.objects.get(pk=self.context.get("main_position"))
            validated_data['main_position'] = main_position_qs

        removed_perms = self.context.get("removed_perms")
        validated_data['removed_perms'] = removed_perms
        instance = super().update(instance, validated_data)
        return instance


class AlbanTushaalTodorhoiloltSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlbanTushaaliinTodorhoilolt
        fields = "__all__"


class AlbanTushaalYeronhiiMedeelelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlbanTushaaliinTodGeneral
        fields = "__all__"


class AlbanTushaaliinChigVvergSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlbanTushaaliinZoriltiinVvreg
        fields = "__all__"


class AlbanTushaaliinZorilgoZoriltSerializer(serializers.ModelSerializer):
    chig_vvreg  = serializers.SerializerMethodField()
    class Meta:
        model = AlbanTushaaliinZorilt
        fields = "__all__"

    def get_chig_vvreg(self, obj):
        chigvvreg_qs = AlbanTushaaliinZoriltiinVvreg.objects.filter(zorilt=obj.id)
        child = AlbanTushaaliinChigVvergSerializer(instance=chigvvreg_qs, many=True).data
        return child

    def create(self, validated_data):
        instance = super().create(validated_data)
        zorilt = self.context['zorilt']

        for inner_list in zorilt['chig_vvreg']:
            inner_list['zorilt'] = instance.id
            serializer_chig_vvreg = AlbanTushaaliinChigVvergSerializer(data=inner_list)
            if serializer_chig_vvreg.is_valid():
                serializer_chig_vvreg.save()

        return instance

    def update(self, instance, validated_data):
        instanced = super().update(instance, validated_data)
        zorilt = self.context['zorilt']

        for chig_vvreg in zorilt['chig_vvreg']:
            chig_vvreg['zorilt'] = instanced.id
            if 'id' in chig_vvreg:
                object_chig = AlbanTushaaliinZoriltiinVvreg.objects.get(id=chig_vvreg['id'])
                serializer_chig_vvreg = AlbanTushaaliinChigVvergSerializer(instance=object_chig, data=chig_vvreg)
                if serializer_chig_vvreg.is_valid():
                    serializer_chig_vvreg.save()
            else:
                serializer_chig_vvreg = AlbanTushaaliinChigVvergSerializer(data=chig_vvreg)
                if serializer_chig_vvreg.is_valid():
                    serializer_chig_vvreg.save()

        return instanced


class AlbanTushaaliinZorilgoSerializer(serializers.ModelSerializer):
    zorilt  = serializers.SerializerMethodField()
    class Meta:
        model = AlbanTushaaliinTodZorilgo
        fields = "__all__"

    def get_zorilt(self, obj):
        zorilt_qs = AlbanTushaaliinZorilt.objects.filter(zorilgo=obj.id)
        child = AlbanTushaaliinZorilgoZoriltSerializer(instance=zorilt_qs, many=True).data
        return child


class AlbanTushaalShaardlagaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlbanTushaalShaardlaga
        fields = "__all__"


class AlbanTushaaliinSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlbanTushaalSubject
        fields= "__all__"


class AlbanTushaalBatalgaajuulaltSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlbanTushaalBatalgaajuulalt
        fields = "__all__"


class AlbanTushaalTodorhoiloltGetSerializer(serializers.ModelSerializer):
    batalgaajuulalt = AlbanTushaalBatalgaajuulaltSerializer()
    general = AlbanTushaalYeronhiiMedeelelSerializer()
    shaardlaga = AlbanTushaalShaardlagaSerializer()
    subject = AlbanTushaaliinSubjectSerializer()
    zorilgo_zorilt = AlbanTushaaliinZorilgoSerializer()

    class Meta:
        model = AlbanTushaaliinTodorhoilolt
        fields = "__all__"
