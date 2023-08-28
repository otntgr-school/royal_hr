from rest_framework import serializers

from django.db.models import Sum

from core.models import KpiIndicator
from core.models import OrgPosition
from core.models import KpiIndicatorAssessment
from core.models import Employee

class KpiIndicatorSerializer(serializers.ModelSerializer):

    class Meta:
        model = KpiIndicator
        fields = '__all__'


class KpiIndicatorAssessmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = KpiIndicatorAssessment
        fields = '__all__'


class KpiIndicatorJsonSerializer(serializers.ModelSerializer):

    ogogdliin_torol = serializers.CharField(source="get_ogogdliin_torol_display")

    class Meta:
        model = KpiIndicator
        fields = '__all__'


class PositionsTreeSerializer(serializers.ModelSerializer):
    """ Албан тушаалын мод хэлбэртэй авах """

    type = serializers.IntegerField(source="id")
    text = serializers.CharField(source="name")
    a_attr = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = OrgPosition
        fields = "__all__"


    def get_a_attr(self, obj):

        return {
            "href": f"/kpi/register/{str(obj.id)}/"
        }


class EmployeeKpiReportJson(serializers.ModelSerializer):

    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    org_name = serializers.SerializerMethodField()
    sub_org_name = serializers.SerializerMethodField()
    salbar_name = serializers.SerializerMethodField()
    org_position_name = serializers.SerializerMethodField()
    statistic = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = "__all__"

    def get_first_name(self, obj):
        return obj.first_name

    def get_last_name(self, obj):
        return obj.last_name

    def get_org_name(self, obj):
        return obj.org.name

    def get_sub_org_name(self, obj):
        return obj.sub_org.name if obj.sub_org else '-'

    def get_salbar_name(self, obj):
        return obj.salbar.name if obj.salbar else '-'

    def get_org_position_name(self, obj):
        return obj.org_position.name if obj.org_position else '-'

    def get_statistic(self, obj):

        request = self.context['request']

        all_data = {
            'm1': 0,
            'm2': 0,
            'm3': 0,
            'q1': 0,
            'm4': 0,
            'm5': 0,
            'm6': 0,
            'q2': 0,
            'h1': 0,
            'm7': 0,
            'm8': 0,
            'm9': 0,
            'q3': 0,
            'm10': 0,
            'm11': 0,
            'm12': 0,
            'q4': 0,
            'h2': 0,
            'y': 0,
        }
        year = request.GET.get('date')

        employee_id = obj.id

        kpiAssessment = KpiIndicatorAssessment.objects.filter(
            employee__id=employee_id,
            created_at__year=year,
        )

        if not kpiAssessment:
            return all_data

        m1 = kpiAssessment.filter(created_at__month=1).aggregate(Sum('onoo')).get('onoo__sum')
        m2 = kpiAssessment.filter(created_at__month=2).aggregate(Sum('onoo')).get('onoo__sum')
        m3 = kpiAssessment.filter(created_at__month=3).aggregate(Sum('onoo')).get('onoo__sum')
        m4 = kpiAssessment.filter(created_at__month=4).aggregate(Sum('onoo')).get('onoo__sum')
        m5 = kpiAssessment.filter(created_at__month=5).aggregate(Sum('onoo')).get('onoo__sum')
        m6 = kpiAssessment.filter(created_at__month=6).aggregate(Sum('onoo')).get('onoo__sum')
        m7 = kpiAssessment.filter(created_at__month=7).aggregate(Sum('onoo')).get('onoo__sum')
        m8 = kpiAssessment.filter(created_at__month=8).aggregate(Sum('onoo')).get('onoo__sum')
        m9 = kpiAssessment.filter(created_at__month=9).aggregate(Sum('onoo')).get('onoo__sum')
        m10 = kpiAssessment.filter(created_at__month=10).aggregate(Sum('onoo')).get('onoo__sum')
        m11 = kpiAssessment.filter(created_at__month=11).aggregate(Sum('onoo')).get('onoo__sum')
        m12 = kpiAssessment.filter(created_at__month=12).aggregate(Sum('onoo')).get('onoo__sum')

        m1 = m1 if m1 else 0
        m2 = m2 if m2 else 0
        m3 = m3 if m3 else 0
        m4 = m4 if m4 else 0
        m5 = m5 if m5 else 0
        m6 = m6 if m6 else 0
        m7 = m7 if m7 else 0
        m8 = m8 if m8 else 0
        m9 = m9 if m9 else 0
        m10 = m10 if m10 else 0
        m11 = m11 if m11 else 0
        m12 = m12 if m12 else 0

        all_data['m1'] = m1
        all_data['m2'] = m2
        all_data['m3'] = m3
        all_data['m4'] = m4
        all_data['m5'] = m5
        all_data['m6'] = m6
        all_data['m7'] = m7
        all_data['m8'] = m8
        all_data['m9'] = m9
        all_data['m10'] = m10
        all_data['m11'] = m11
        all_data['m12'] = m12
        all_data['q1'] = m1 + m2 + m3
        all_data['q2'] = m4 + m6 + m5
        all_data['q3'] = m7 + m8 + m9
        all_data['q4'] = m10 + m11 + m12
        all_data['h1'] = m1 + m2 + m3 + m4 + m6 + m5
        all_data['h2'] = m7 + m8 + m9 + m10 + m11 + m12
        all_data['y'] = m1 + m2 + m3 + m4 + m6 + m5 + m7 + m8 + m9 + m10 + m11 + m12

        return all_data
