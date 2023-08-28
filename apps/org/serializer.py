from django.db.models import Q

from rest_framework import serializers

from core.models import Orgs
from core.models import WorkAdsense
from core.models import Permissions
from core.models import Roles
from core.models import OrgPosition
from core.models import User
from core.models import Employee


class OrgsSerializer(serializers.ModelSerializer):
    """байгууллагын мэдээллийг бүртгэх нь
    """
    text = serializers.CharField(source="name", label="Нэр", style={ "placeholder": "Нэр оруулна уу" })
    a_attr = serializers.SerializerMethodField()

    class Meta:
        model = Orgs
        exclude = "name",

    def get_a_attr(self, obj):
        return{
            "href": f"/org/org-register/{str(obj.id)}/"
        }

    @staticmethod
    def create_defualt_role(name, description, permissions_names, org_id):
        try:
            org_position=''

            role = Roles.objects.filter(name=name).first()
            if role:
                is_hr = False
                is_director = False
                if role.name.lower() == 'хүний нөөц':
                    is_hr = True
                if role.name.lower() == 'удирдах ажилтан':
                    is_director = True
                org_position = OrgPosition.objects.create(
                    name=name,
                    description=description,
                    org_id=org_id,
                    is_hr=is_hr,
                    is_director=is_director
                )
                org_position.roles.add(role)
            else:
                permissions = None
                filters = Q()
                permissions_list = []
                for role_name in permissions_names.split(','):
                    if role_name:
                        permissions_list.append(str(role_name.strip()))

                if 'main' in  permissions_list:
                    filters.add(Q(name__endswith='main'), Q.OR)
                    permissions_list.remove('main')
                if 'read' in  permissions_list:
                    filters.add(Q(name__endswith='read'), Q.OR)
                    permissions_list.remove('read')
                if 'create' in  permissions_list:
                    filters.add(Q(name__endswith='create'), Q.OR)
                    permissions_list.remove('create')
                if 'update' in  permissions_list:
                    filters.add(Q(name__endswith='update'), Q.OR)
                    permissions_list.remove('update')
                if 'delete' in  permissions_list:
                    filters.add(Q(name__endswith='delete'), Q.OR)
                    permissions_list.remove('delete')
                if 'refuse' in  permissions_list:
                    filters.add(Q(name__endswith='refuse'), Q.OR)
                    permissions_list.remove('refuse')
                if 'edit' in  permissions_list:
                    filters.add(Q(name__endswith='edit'), Q.OR)
                    permissions_list.remove('edit')
                if 'approve' in  permissions_list:
                    filters.add(Q(name__endswith='approve'), Q.OR)
                    permissions_list.remove('approve')
                if 'restore' in  permissions_list:
                    filters.add(Q(name__endswith='restore'), Q.OR)
                    permissions_list.remove('restore')

                filters.add(Q(name__in=permissions_list), Q.OR)

                if filters:
                    permissions = Permissions.objects.filter(filters)
                role_new = Roles.objects.create(name=name, description=description)

                if permissions:
                    role_new.permissions.set(permissions)

                if role_new:
                    org_position = OrgPosition.objects.create(name=name, description=description, org_id=org_id)
                    org_position.roles.set(role_new)
            return True
        except:
            return False


#бүртгэгдсэн байгууллага авах нь
class OrgJsonSerializer(serializers.ModelSerializer):
    text = serializers.CharField(source='name')
    type = serializers.CharField(source='id')
    state = serializers.SerializerMethodField()
    a_attr = serializers.SerializerMethodField()

    class Meta:
        model = Orgs
        fields = ['text', 'type','state', 'a_attr']

    def get_a_attr(self, obj):
        return{
            "href": f"/org/org-register/{str(obj.id)}/"
        }


    def get_state(self, obj):
        """ анх ороход нээгдсэн байдлаар харуулах """

        return {
            "opened": True
        }


class UserFirstRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = 'email', 'phone_number'


class UserSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = 'email', 'phone_number', 'password'

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)

        instance.save()

        return instance


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = 'user', 'org', 'org_position'


class EmailOrgSerializer(serializers.ModelSerializer):

    class Meta:
        model = Orgs
        fields = "id", "email_host_user", "email_use_tls", "email_host_name", "email_host", "email_port", "email_password"
