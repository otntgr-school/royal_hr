from django.urls import reverse

from rest_framework import serializers

from core.models import (
    WorkCalendar,
    WorkCalendarKind,
    Employee
)


class WorkCalendarKindFormSerializer(serializers.ModelSerializer):

    title = serializers.CharField(label="Гарчиг")
    textColor = serializers.CharField(style={ "input_type": "color" }, label="Бичигний өнгө")
    color = serializers.CharField(style={ "input_type": "color" }, label="Арын өнгө")

    class Meta:
        model = WorkCalendarKind
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


class WorkCalendarKindListSerializer(serializers.ModelSerializer):

    text = serializers.CharField(source="title", default="")
    type = serializers.IntegerField(source="id")
    a_attr = serializers.SerializerMethodField()

    class Meta:
        model = WorkCalendarKind
        fields = "type", "id", 'text', 'a_attr'

    def get_a_attr(self, obj):
        return {
            "href": reverse("work-calendar-kinds", args=(obj.id,))
        }


class WorkCalendarFormSerializer(serializers.ModelSerializer):

    url = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    employees = serializers.PrimaryKeyRelatedField(allow_empty=True, label='Хэрэглэгчид', many=True, queryset=Employee.objects.all())

    class Meta:
        model = WorkCalendar
        fields = "__all__"

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data.update(request.exactly_org_filter)

        return super().create(validated_data)


class WorkCalendarListSerializer(serializers.ModelSerializer):

    textColor = serializers.CharField(source="kind.textColor", default="")
    color = serializers.CharField(source="kind.color", default="")
    title = serializers.CharField(source="kind.title", default="")
    work_title = serializers.CharField(source="title")
    start = serializers.DateTimeField(source="start_date")
    end = serializers.DateTimeField(source="end_date")
    url = serializers.SerializerMethodField()
    formUrl = serializers.SerializerMethodField()
    cid = serializers.IntegerField(source="id")
    today_time = serializers.SerializerMethodField()

    class Meta:
        model = WorkCalendar
        fields = "__all__"

    def get_url(self, obj):
        return obj.url if obj.url else ""

    def get_formUrl(self, obj):
        return reverse('work-calendar-form', args=(obj.id,))

    def get_today_time(self, obj):
        return str(obj.start_date.strftime('%H:%M')) + " - " +str(obj.end_date.strftime('%H:%M'))
