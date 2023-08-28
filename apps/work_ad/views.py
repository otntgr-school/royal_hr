import json
import datetime

from django.core.paginator import Paginator
from django.db.models import Value
from django.db.models import F
from django.db.models.functions import Concat
from django.db.models.functions import Substr
from django.db.models.functions import Upper
from django.urls import reverse

from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from core.models import ChigluulehHutulbur, Notification, WorkAdsense
from core.models import WorkJoinRequests
from core.models import Salbars
from core.models import Command
from core.models import Employee
from core.models import UserInfo
from core.models import User
from core.models import OrgPosition
from core.models import CountNumber

from .serializer import WorkAdsenseSerializer
from .serializer import WorkJoinRequestsSerializer
from .serializer import WorkJoinRequestSerializer
from .serializer import WorkRqPagniateSerializer
from .serializer import WorkJoinRequestV2Serializer
from .serializer import WorkAdsenseOrgSerializer
from .serializer import WorkAdsenseOrgPaginateSerializer
from apps.worker.serializer import EmployeeSerializer
from apps.worker.serializer import EmployeeMigrationsSerializer
from apps.worker.serializer import ChigluulehSerializer
from core.fns import WithChoices

from main.utils.encrypt import decrypt
from main.utils.datatable import data_table
from main.utils.user_percent import CalcUserPercent


class WorkAdsenseListApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/work-ad-sense/user/workadsenseList/index.html'

    def get(self, request):
        return Response()


class WorkAdsenseGetApiView(APIView):

    def get(self, request):

        skip = int(request.GET.get('skip'))
        limit = int(request.GET.get('limit'))

        qs = WorkAdsense.objects.filter(state=WorkAdsense.ACTIVE).order_by('-created_at')[skip:skip + limit]
        serializer = WorkAdsenseSerializer(instance=qs, many=True, context={"request": request}).data
        qs = WorkAdsense.objects.filter(state=WorkAdsense.ACTIVE)
        paginator = Paginator(qs, limit)

        return request.send_data({
            "total_pages": paginator.num_pages,
            "serializer": serializer
        })


class WorkJoinRequest(APIView):

    def get(self, request):
        work_adsense_id = int(request.GET.get("work_adsense_id"))

        objectz = WorkAdsense.objects.get(pk=work_adsense_id)
        serializerz = WorkAdsenseSerializer(instance=objectz, context={"request": request})

        return request.send_data({
            "adsense": serializerz.data
        })

    def post(self, request):
        request.data['user'] = request.user.pk
        serializer = WorkJoinRequestsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return request.send_info("INF_013")
        return request.send_error_valid(serializer.errors)


class UserWorkJoinRequest(APIView):

    def get(self, request, state=None):

        extra_filter = dict()
        if state:
            extra_filter['state'] = state

        qs = WorkJoinRequests \
                .objects \
                .filter(
                    user=request.user,
                    **extra_filter
                ) \
                .annotate(
                    org_name=F("org__name"),
                    org_position_name=F("org_position__name")
                )

        paginated = data_table(qs, request)
        paginated['data'] = WorkJoinRequestSerializer(paginated['data'], many = True).data
        return Response(paginated)

    def delete(self, request, pk):
        obj = WorkJoinRequests.objects.get(id=pk)
        obj.state = WorkJoinRequests.DECLINED_BY_MYSELF
        obj.save()
        return request.send_info("INF_007")


class MyJoinRequestsApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/work-ad-sense/user/my-work-requests/index.html'

    def get(self, request):
        return Response({
            'request_states': WorkJoinRequests.STATE_STATUS,
        })


class WorkAdsenseRequestsApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/work-ad-sense/org/work-adsense-requests/index.html'

    def get(self, request):
        tree_data, pos = Salbars.get_tree(request)
        org_position_list = list(
            OrgPosition
                .objects
                .filter(
                    org=request.employee.org
                )
                .values('id', 'name')
        )
        command_list = Command.objects.filter(**request.org_filter).values('id', 'name', 'command_number')

        return Response(
        {
            'request_states': WorkJoinRequests.STATE_STATUS,
            'tree_data': json.dumps(list(tree_data)),
            'pos': pos,
            'org_positions': org_position_list,
            'command': command_list,
            "worker_type": Employee.WORKER_TYPE,
        })


class WorkAdsensePaginate(APIView):
    def get(self, request, pk=None, state=None):

        extra_filter = dict()
        if state:
            extra_filter['state'] = state

        qs = WorkJoinRequests \
                .objects \
                .filter(
                    org=request.org_filter['org'],
                    user__userinfo__action_status=UserInfo.APPROVED,
                    user__userinfo__action_status_type=UserInfo.ACTION_TYPE_ALL,
                    **extra_filter,
                ) \
                .annotate(
                    full_name=Concat(Upper(Substr("user__userinfo__last_name", 1, 1)), Value(". "), "user__userinfo__first_name"),
                    state_name=WithChoices(WorkJoinRequests.STATE_STATUS, "state"),
                    org_position_name=F("org_position__name")
                )

        paginated = data_table(qs, request)
        paginated['data'] = WorkRqPagniateSerializer(paginated['data'], many=True).data
        return Response(paginated)

    def post(self, request, pk=None):

        token= request.data['token']

        real_pk = decrypt(token)
        obj = WorkJoinRequests.objects.get(id=real_pk)

        request.data['org_position'] = obj.org_position.id
        request.data['org_position_id'] = obj.org_position.id

        if "org" in request.org_filter:
            request.data['org_id'] = request.org_filter['org'].id
        if "sub_org" in request.org_filter:
            request.data['sub_org_id'] = request.org_filter['sub_org'].id
        if "salbar" in request.org_filter:
            request.data['salbar_id'] = request.org_filter['salbar'].id

        request.data['user'] = obj.user.id
        request.data['work_adsense'] = obj.work_adsense.id
        request.data['state'] = WorkJoinRequests.DECLINED

        serializer = WorkJoinRequestV2Serializer(instance=obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return request.send_info("INF_007")
        return request.send_error_valid(serializer.errors)


class RequestedManApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/worker/hrUpdateProfile/index.html'

    def get(self, request):
        token = request.GET.get("token")
        real_pk = decrypt(token)
        join_request_obj = WorkJoinRequests.objects.get(id=real_pk)
        userinfo = UserInfo.objects.get(user_id=join_request_obj.user.id, action_status=UserInfo.APPROVED, action_status_type=UserInfo.ACTION_TYPE_ALL)
        p_percent = CalcUserPercent.display_progress_percent(user=join_request_obj.user)
        return Response({
            'selected_user_data': join_request_obj.user,
            'selected_userinfo_data': userinfo,
            'join_req': "True",
            "p_percent": p_percent,

        })


class CreateEmployeeApiView(APIView):

    def post(self, request):

        if 'user' in request.data:
            employee_body = dict()

            join_request_id = decrypt(request.data['user'])
            join_request = WorkJoinRequests.objects.filter(id=join_request_id).first()
            if not join_request:
                raise request.send_error("ERR_003")
            user = User.objects.filter(id=join_request.user.id).first()

            # Тухайн хүсэлтийн хэрэглэгч өөр байгуулгат бүртгэл буюу ажилтай байвал шууд ажилд авах боломжгүй
            old_employee = Employee.objects.filter(user=user, state=Employee.STATE_WORKING).first()
            if old_employee:
                return request.send_warning("WRN_007")

            count_number = CountNumber.objects.filter(name='time_register_employee').last()
            time_register_id_count = count_number.count

            employee_body = {
                "user": user.id,
                "org": request.employee.org.id,
                "sub_org": (int(request.data['sub_org']) if request.data['sub_org'] else None) if 'sub_org' in request.data else None,
                "salbar": (int(request.data['salbar']) if request.data['salbar'] else None) if 'salbar' in request.data else None,
                "working_type": request.data['working_type'] if 'working_type' in request.data else None,
                "org_position": request.data['org_position'] if 'org_position' in request.data else None,
                'time_register_employee': time_register_id_count,
            }

            employee_serializer = EmployeeSerializer(data=employee_body)
            if not employee_serializer.is_valid():
                return request.send_error_valid(employee_serializer.errors)

            employee = employee_serializer.save()

            # Ажилтны албан тушаалын шилжилтийн мэдээллийг хадгалах нь
            EmployeeMigrationsSerializer.create_from_employee(employee, None, request.data['command'] if 'command' in request.data else None)

            # Ажилтнаа нэмсний дараа ажилчны тоог нэмнэ
            time_register_id_count = time_register_id_count + 1
            count_number.count = time_register_id_count
            count_number.save()

            # Тухайн хэрэглэгчийн ажилд авах хүсэлтийг зөвшөөрнө
            join_request.state = WorkJoinRequests.APPROVED
            join_request.save()
            # Өөр албан тушаал салбар дээр хүсэлтүүдийг цуцална
            WorkJoinRequests.objects.filter(user=user.id, state=WorkJoinRequests.PENDING).update(state=WorkJoinRequests.DECLINED)

            return request.send_info("INF_002")
        else:
            return request.send_warning("WRN_008")


class WorkAdsenseApiView(APIView):
    """ Эрхүүдийн жагсаалт """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/work-ad-sense/org/workadsense/index.html'

    def get(self, request):
        org_positions_qs = []
        if "org" in request.org_filter:
            org_positions_qs = OrgPosition.objects.filter(org_id=request.org_filter.get("org").id)

        return Response({ "org_positions": org_positions_qs })


class WorkAdsenseCRUDApiView(APIView):

    def post(self, request, pk=None):
        if "org" in request.org_filter:
            request.data['org'] = request.org_filter.get("org").id
        if "sub_org" in request.org_filter:
            request.data['sub_org'] = request.org_filter['sub_org'].id
        if "salbar" in request.org_filter:
            request.data['salbar'] = request.org_filter['salbar'].id

        if 'end_at' in request.data:
            today = datetime.datetime.now()
            if str(today) < request.data['end_at']:
                request.data['state'] = WorkAdsense.ACTIVE
            else:
                request.data['state'] = WorkAdsense.INACTIVE

        serialzer = WorkAdsenseOrgSerializer(data=request.data)
        serialzer.is_valid(raise_exception=True)
        serialzer.save()
        return request.send_info("INF_001")

    def put(self, request, pk):
        if 'end_at' in request.data:
            today = datetime.datetime.now()
            if str(today) < request.data['end_at']:
                request.data['state'] = WorkAdsense.ACTIVE
            else:
                request.data['state'] = WorkAdsense.INACTIVE

        obj = WorkAdsense.objects.get(pk=pk)
        serialzer = WorkAdsenseOrgSerializer(instance=obj, data=request.data)
        serialzer.is_valid(raise_exception=True)
        serialzer.save()
        return request.send_info("INF_002")

    def get(self, request, pk):
        obj = WorkAdsense.objects.get(pk=pk)
        serialzer = WorkAdsenseOrgSerializer(instance=obj)
        return request.send_data(serialzer.data)

    def delete(self, request, pk=None):
        obj = WorkAdsense.objects.get(pk=pk)
        obj.delete()
        return request.send_info("INF_003")


class WorkAdsensePaginateApiView(APIView):

    def get(self, request):
        qs = WorkAdsense.objects.filter(org_id=request.org_filter.get("org").id)\
            .annotate(
                state_name=WithChoices(WorkAdsense.STATE_STATUS, 'state')
            )

        paginated = data_table(qs, request)
        paginated['data'] = WorkAdsenseOrgPaginateSerializer(paginated['data'], many=True).data

        return Response(paginated)


class SendChigluulehApiView(APIView):

    def put(self, request):

        token = str(request.data)
        id = decrypt(token)

        obj = WorkJoinRequests.objects.get(id=id)
        is_send = not obj.is_send_uureg
        obj.is_send_uureg = is_send
        obj.save()

        title = (
            "Танд чиглүүлэх хөтөлбөр илгээсэн байна"
            if is_send
            else
            "Чиглүүлэх хөтөлбөрийг болиулсан байна"
        )
        Notification.objects.create_notif(
            request     = request,
            title       = title,
            content     = f"{obj.org_position.name} -д орох хүсэлтэнд",
            ntype       = 'normal',
            url         = reverse("my-join-requests"),
            scope_kind  = Notification.SCOPE_KIND_USER,
            from_kind   = Notification.FROM_KIND_ORG,
            scope_ids   = [ obj.user_id ]
        )

        return request.send_info("INF_002")


class GetChigluulehAPIView(APIView):

    def get(self, request, pk):

        work_request = WorkJoinRequests.objects.get(pk=pk)
        if not work_request.is_send_uureg:
            return request.send_error("ERR_013")

        ad_sense = work_request.work_adsense

        filters = {
            'org': ad_sense.org,
            'sub_org': ad_sense.sub_org,
            'salbar': ad_sense.salbar,
        }

        hutulburs = ChigluulehHutulbur.objects.filter(**filters)
        data = ChigluulehSerializer(hutulburs, many=True, context={ "public": True }).data
        return request.send_data(data)


def anyEndedWorkAdsense():
    work_adsense_update= []
    work_adsense_list = WorkAdsense.objects.filter(state=WorkAdsense.ACTIVE, end_at__lte=str(datetime.datetime.now()))

    for work_adsense in work_adsense_list:
        work_adsense.state = WorkAdsense.INACTIVE
        work_adsense_update.append(work_adsense)

    if len(work_adsense_update) > 0:
        WorkAdsense.objects.bulk_update(work_adsense_update, ['state'])
