
from rest_framework import serializers

from core.models import SubOrgs
from core.models import Orgs


class SubOrgsSerializer(serializers.ModelSerializer):

    @staticmethod
    def get_filters(request):
        """ SubOrg ийг хайхад хэрэгтэй filter үүд байна
            org filter ээс ялгаж авсан байгаа
        """
        filters = {
            "org": request.org_filter.get("org")
        }

        if request.org_filter.get("sub_org"):
            filters['id'] = request.org_filter.get("sub_org").id

        return filters

    class Meta:
        model = SubOrgs
        exclude = "org",


class SubOrgsCRSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubOrgs
        fields = "__all__"


class OrgsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orgs
        fields = '__all__'


class SubOrgsJsonSerializer(serializers.ModelSerializer):

    text = serializers.CharField(source="name")
    type = serializers.CharField(source="id")
    a_attr = serializers.SerializerMethodField()

    class Meta:
        model = SubOrgs
        fields = ['text', 'type', 'a_attr']

    def get_a_attr(self, obj):
        return {
            "href": f"/suborg/sub-company-register/{str(obj.id)}/"
        }


class OrgsJsonSerializer(serializers.ModelSerializer):

    children = serializers.SerializerMethodField()
    text = serializers.CharField(source='name')
    type = serializers.CharField(source='id')
    state = serializers.SerializerMethodField()

    class Meta:
        model = Orgs
        fields = ['text', 'type', 'children', 'state']

    def get_children(self, obj):
        request = self.context.get("request")
        sub_org = request.org_filter.get("sub_org")

        filters = {}
        if sub_org:
            filters['id'] = sub_org.id

        instance = obj.suborgs_set.filter(**filters)
        child = SubOrgsJsonSerializer(instance=instance, many=True).data
        ##  зөвхөн хамгийн том байгууллагын хүн дэд байгууллага нэмнэ
        if request.org_lvl > 2:
            child.append(
                {
                    "text": "Шинээр үүсгэх",
                    "a_attr": {
                        "href": "/suborg/sub-company-register/"
                    },
                    "icon": "fa fa-folder-plus"
                }
            )
        return child

    def get_state(self, obj):
        """ анх ороход нээгдсэн байдлаар харуулах """

        return {
            "opened": True
        }
