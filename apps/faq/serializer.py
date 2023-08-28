from django.urls import reverse

from rest_framework import serializers

from core.models import FAQ, FAQGroup

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQGroup
        fields = "__all__"


class FAQGroupPageSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source="get_type_display")
    class Meta:
        model = FAQGroup
        fields = "__all__"


class FAQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = "__all__"


class FAQuestionPaginateSerializer(serializers.ModelSerializer):
    group = serializers.CharField(source="group.name")
    class Meta:
        model = FAQ
        fields = "__all__"


class FAQListSerializer(serializers.ModelSerializer):
    questions  = serializers.SerializerMethodField()
    class Meta:
        model = FAQGroup
        fields = "__all__"

    def get_questions(self, obj):
        zorilt_qs = FAQ.objects.filter(group_id=obj.id)
        child = FAQuestionSerializer(instance=zorilt_qs, many=True).data
        return child
