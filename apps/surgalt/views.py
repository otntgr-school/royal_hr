from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from django.db.models import Q

from core.models import Surgalt, UserInfo
from core.models import Employee
from core.fns import WithChoices

from .serializer import SurgaltSerializer
from .serializer import SurgaltPaginationSerializer

from main.decorators import login_required
from main.utils.datatable import data_table
from main.decorators import has_permission


class SurgaltPaginationViews(APIView):

    @login_required()
    @has_permission(must_permissions=['surgalt-read'])
    def get(self, request, pk=None):

        if pk:
            surgalt = Surgalt.objects.filter(
                **request.org_filter,
                pk=pk
            ) \
            .annotate(
                for_type_name=WithChoices(Surgalt.FOR_TYPE_CHOICES, 'for_type'),
            ) \
            .first()

            if not surgalt:
                raise request.send_error("ERR_013")

            data = SurgaltPaginationSerializer(surgalt, many=False).data
            return request.send_data(data)

        extra_filter = Q(**request.org_filter)

        if 'surgalt-all-read' not in request.permissions:
            extra_filter.add(Q(employees__in=[request.employee]) | Q(for_type=Surgalt.FOR_WHOLE), Q.AND)

        qs = Surgalt.objects\
            .filter(
                extra_filter
            )\
            .annotate(
                for_type_name=WithChoices(Surgalt.FOR_TYPE_CHOICES, 'for_type'),
            )

        paginated = data_table(qs, request)
        paginated['data'] = SurgaltPaginationSerializer(paginated['data'], many=True).data

        return Response(paginated)


class SurgaltListAPIView(APIView):
    """ Ажилчидын жагсаалт хуудас """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/surgalt/surgalt-list.html'

    @login_required()
    @has_permission(must_permissions=['surgalt-read'])
    def get(self, request):

        employees = Employee.objects.filter(
            **request.org_filter,
            state=Employee.STATE_WORKING,
            user__userinfo__action_status=UserInfo.APPROVED,
            user__userinfo__action_status_type=UserInfo.ACTION_TYPE_ALL
        ).order_by('user__userinfo__first_name')

        return Response({
            "info": {
                "total_employee": employees.count(),
                "for_type": Surgalt.FOR_TYPE_CHOICES,
                "employees": employees,
            },
        })


class SurgaltCreateEditApiView(APIView):

    queryset = Surgalt.objects
    serializer_class = SurgaltSerializer

    @login_required()
    @has_permission(must_permissions=['surgalt-create'])
    def post(self, request):
        more_info = dict()          # Нэмэлт дата
        more_info = {
            "org": request.org_filter['org'].id if 'org' in request.org_filter else None,
            "sub_org": request.org_filter['sub_org'].id if 'sub_org' in request.org_filter else None,
            "salbar": request.org_filter['salbar'].id if 'salbar' in request.org_filter else None,
        }

        serializer = self.serializer_class(data={ **request.data, **more_info})
        if not serializer.is_valid():
            return request.send_error_valid(serializer.errors)

        serializer.save()

        return request.send_info("INF_001")

    @login_required()
    @has_permission(must_permissions=['surgalt-update'])
    def put(self, request, pk):

        instance = self.queryset.get(pk=pk)
        serializer = self.serializer_class(instance=instance, data=request.data)

        if not serializer.is_valid():
            return request.send_error_valid(serializer.errors)
        serializer.save()

        return request.send_info("INF_002")


class SurgaltDeleteApiView(APIView):

    @login_required()
    @has_permission(must_permissions=['surgalt-delete'])
    def delete(self,request, pk):

        Surgalt.objects.filter(pk=pk).delete()

        return request.send_info("INF_003")
