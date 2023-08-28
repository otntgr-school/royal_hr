from rest_framework import serializers

from core.models import WorkAdsense
from core.models import Orgs
from core.models import WorkJoinRequests

from main.utils.encrypt import encrypt


class OrgSerializer(serializers.ModelSerializer):

    class Meta:
        model = Orgs
        fields = "__all__"


class WorkAdsenseSerializer(serializers.ModelSerializer):

    org  = serializers.SerializerMethodField()
    is_already  = serializers.SerializerMethodField()
    org_position = serializers.CharField(source='org_position.name')
    org_position_id = serializers.IntegerField(source='org_position.id')

    class Meta:
        model = WorkAdsense
        fields = "__all__"

    def get_org(self, obj):
        zorilt_qs = Orgs.objects.get(id=obj.org_id)
        child = OrgSerializer(instance=zorilt_qs).data
        return child

    def get_is_already(self, obj):
        request = self.context['request']
        qs = WorkJoinRequests.objects.filter(
            user=request.user,
            work_adsense=obj,
            state=WorkJoinRequests.PENDING
        ).first()
        if qs:
            return True
        return False


class WorkJoinRequestSerializer(serializers.ModelSerializer):

    state = serializers.CharField(source='get_state_display')
    org_name = serializers.SerializerMethodField()
    org_position_name = serializers.SerializerMethodField()

    class Meta:
        model = WorkJoinRequests
        fields = "__all__"

    def get_org_name(self, obj):
        return obj.org_name

    def get_org_position_name(self, obj):
        return obj.org_position_name


class WorkJoinRequestV2Serializer(serializers.ModelSerializer):

    class Meta:
        model = WorkJoinRequests
        fields = "__all__"


class WorkJoinRequestsSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkJoinRequests
        fields = "__all__"


class WorkRqPagniateSerializer(serializers.ModelSerializer):

    org_position_name = serializers.SerializerMethodField()
    org_position_id = serializers.CharField(source='org_position.id', default="")
    id = serializers.SerializerMethodField()
    state_name = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = WorkJoinRequests
        fields = "__all__"

    def get_id(self, obj):
        return encrypt(obj.id)

    def get_state_name(self, obj):
        return obj.state_name

    def get_full_name(self, obj):
        return obj.full_name

    def get_org_position_name(self, obj):
        return obj.org_position_name


class WorkAdsenseOrgSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkAdsense
        fields = "__all__"


class WorkAdsenseOrgPaginateSerializer(serializers.ModelSerializer):

    org_position = serializers.CharField(source="org_position.name")
    state_name = serializers.SerializerMethodField()

    class Meta:
        model = WorkAdsense
        fields = "__all__"

    def get_state_name(self, obj):
        return obj.state_name
