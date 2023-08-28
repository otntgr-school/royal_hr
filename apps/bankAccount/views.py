from django.shortcuts import redirect

from rest_framework import mixins
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer

from core.fns import WithChoices
from django.db import transaction
from django.db.models import Max
from django.db.models import F
from django.db.models import Q

from core.models import (
    BankAccountRequest,
    BankAccountInfo,
    BankInfo,
    Employee,
    User,
    UserInfo,
)

from .serializer import BankInfoSerializer
from .serializer import BankAccountInfoSerializer
from .serializer import BankAccountRequestSerializer

from main.decorators import login_required
from main.utils.datatable import data_table
from main.decorators import has_permission


class BankInfoApiView(APIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/bankAccount/create-bank.html'

    queryset = BankInfo.objects
    serializer_class = BankInfoSerializer

    def get_response(self, serializer, pk=None):
        return Response(
            {
                "serializer": serializer,
                "pk": pk
            }
        )

    @login_required(is_superuser=True)
    def get(self, request, pk=None):

        if pk:
            qs = self.queryset.get(pk=pk)
            serializer = self.serializer_class(instance=qs)
            return self.get_response(serializer, pk)

        serializer = self.serializer_class()
        return self.get_response(serializer)

    @login_required(is_superuser=True)
    def post(self, request, pk=None):
        if pk:
            if not request.data['image']:
                request.data._mutable = True
                request.data.pop('image')
                request.data._mutable = False

            qs = self.queryset.get(pk=pk)
            serializer = self.serializer_class(instance=qs, data=request.data)
            if serializer.is_valid():
                # Өмнөх зураг байгаа эсэхийг шалгаад устгах
                try:
                    request.data['image']
                    if qs.image:
                        qs.image.delete()
                except:
                    None

                serializer.save()
                request.send_message("success", 'INF_002')

            return redirect("static-bank")

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            request.send_message("error", "ERR_001")
            return Response(
                {
                    'serializer': self.serializer_class,
                }
            )

        serializer.save()

        request.send_message("success", 'INF_001')

        return redirect("static-bank")


class BankInfoListApiView(APIView):

    @login_required(is_superuser=True)
    def get(self, request):

        banks_info = BankInfo.objects.all().values("id", 'name', 'image', 'order').order_by("order")
        return request.send_data(banks_info)


class BankInfoDeleteApiView(
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):

    queryset = BankInfo.objects
    serializer_class = BankAccountInfoSerializer

    @login_required(is_superuser=True)
    def get(self, request, pk):
        # Өмнөх зураг байгаа эсэхийг шалгаад устгах
        qs = self.queryset.get(pk=pk)
        try:
            if qs.image:
                qs.image.delete()
        except:
            pass

        self.destroy(request)
        request.send_message("success", 'INF_003')

        return redirect("static-bank")


class BankInfoChangeOrder(APIView):

    @login_required(is_superuser=True)
    @transaction.atomic()
    def put(self, request):

        from_id = request.data.get("from_id")
        to_id = request.data.get("to_id")

        if not from_id:
            ## warning bolgoh
            raise request.send_error("ERR_013")

        _from_qs = BankInfo.objects.filter(id=from_id)
        #  фронтоос хамгийн доор байрлуулахад id ирэхгүй байгаа учраас түүнийг хайж олох нь
        if not to_id:
            _to = BankInfo.objects.aggregate(most_max=Max("order"))['most_max']
        else:
            _to_qs = BankInfo.objects.filter(id=to_id)
            if not _to_qs:
                ## warning bolgoh
                raise request.send_error("ERR_013")
            _to = _to_qs.first().order

        if not _from_qs:
            ## warning bolgoh
            raise request.send_error("ERR_013")

        _from = _from_qs.first().order

        is_down = _from < _to
        _range = [_from, _to] if is_down else [_to, _from]

        changes = []

        qs = BankInfo.objects.filter(id=from_id, order=_from)
        if qs:
            qs.update(order=_to)
            changes.append([_from, _to, from_id])
            datas = BankInfo.objects.filter(order__range=_range).exclude(id=from_id).order_by('order')
            for item in datas:
                start = item.order
                item.order = item.order - 1 if is_down else item.order + 1
                end = item.order
                changes.append([start, end, item.id])
                item.save()
        else:
            ## warning bolgoh
            raise request.send_error("ERR_013")

        return request.send_rsp("INF_002", changes)


class BankAccountInfoApiView(
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):

    queryset = BankAccountInfo.objects
    serializer_class = BankAccountInfoSerializer

    def set_orgs_and_more(self, request):
        org = None
        sub_org = None
        salbar = None
        if "org" in request.org_filter:
            org = request.org_filter['org'].id
        if "sub_org" in request.org_filter:
            sub_org = request.org_filter['sub_org'].id
        if "salbar" in request.org_filter:
            salbar = request.org_filter['salbar'].id

        return org, sub_org, salbar

    def post(self, request, pk=None):

        check = BankAccountInfo.objects.filter(number=request.data['number'])
        if check:
            return request.send_warning("WRN_009", [], "данс")

        # Хэрэв pk байвал хүний нөөц шууд тухайн хэрэглэгчийн мэдээллийг үүсгэж байна гэж үзээд  баазд бүртгэнэ
        if pk:
            user = User.objects.filter(pk=pk).first()
            if user:
                account_body = {
                    "bank": request.data['bankInfoSelect'],
                    "number": request.data['number'],
                    "user": user.id,
                }

                serializer = self.serializer_class(data=account_body)
                if not serializer.is_valid():
                    return request.send_error_valid(serializer.errors)

                serializer.save()
            else:
                return request.send_error_valid(serializer.errors)

            return request.send_rsp("INF_001", '')

        # Хэрэв хэрэглэгч байгуулгад бүртгэлгүй бол шууд тухайн датаг баазд бүртгэнэ.
        elif not request.employee or request.employee.is_hr:
            account_body = {
                "bank": request.data['bankInfoSelect'],
                "number": request.data['number'],
                "user": request.user.id,
            }

            serializer = self.serializer_class(data=account_body)
            if not serializer.is_valid():
                return request.send_error_valid(serializer.errors)

            serializer.save()
            return request.send_rsp("INF_001", '')
        # Дээрх нөхцөлүүд биелээгүй бол тухайн хүсэлт гаргагчийг ажилтанг гэж үзээд өөрчлөх хүсэлт хүний нөөцлүү явуулна.
        else:
            org_id, sub_org_id, salbar_id = self.set_orgs_and_more(request)

            bank_request_body = {
                "bank": request.data['bankInfoSelect'],
                "number": request.data['number'],
                "employee": request.employee.id,
                "state": BankAccountRequest.CREATE,
                "org": org_id,
                "sub_org": sub_org_id,
                "salbar": salbar_id
            }

            serializer = BankAccountRequestSerializer(data=bank_request_body)
            if not serializer.is_valid():
                return request.send_error_valid(serializer.errors)

            serializer.save()
            return request.send_rsp("INF_013", '')

    def put(self, request, pk=None, userId=None):
        check = BankAccountInfo.objects.filter(number=request.data['editNumber'])
        if check:
            return request.send_warning("WRN_009", [], "данс")

        # Хэрэв pk байвал хүний нөөц шууд тухайн хэрэглэгчийн мэдээллийг үүсгэж байна гэж үзээд  баазд бүртгэнэ
        if userId:
            user = User.objects.filter(pk=userId).first()
            if user:
                account_body = {
                    "bank": request.data['editBankInfoSelect'],
                    "number": request.data['editNumber'],
                    "user": user.id,
                }

                queryset = self.queryset.get(pk=pk)
                serializer = self.serializer_class(instance=queryset, data=account_body)
                if not serializer.is_valid():
                    return request.send_error_valid(serializer.errors)

                serializer.save()
            else:
                return request.send_error_valid(serializer.errors)

            return request.send_rsp("INF_002", '')

        # Хэрэв хэрэглэгч байгуулгад бүртгэлгүй бол шууд тухайн датаг баазд бүртгэнэ.
        if pk and not request.employee or request.employee.is_hr:
            account_body = {
                "bank": request.data['editBankInfoSelect'],
                "number": request.data['editNumber'],
                "user": request.user.id
            }

            queryset = self.queryset.get(pk=pk)
            serializer = self.serializer_class(instance=queryset, data=account_body)
            if not serializer.is_valid():
                return request.send_error_valid(serializer.errors)

            serializer.save()
            return request.send_rsp("INF_002", '')
        # Дээрх нөхцөлүүд биелээгүй бол тухайн хүсэлт гаргагчийг ажилтанг гэж үзээд өөрчлөх хүсэлт хүний нөөцлүү явуулна.
        else:
            account_data = self.queryset.filter(pk=pk).first()
            if account_data:
                org_id, sub_org_id, salbar_id = self.set_orgs_and_more(request)
                bank_request_body = {
                    "bank": request.data['editBankInfoSelect'],
                    "number": request.data['editNumber'],
                    "employee": request.employee.id,
                    "state": BankAccountRequest.UPDATE,
                    "bank_account": account_data.id,
                    "org": org_id,
                    "sub_org": sub_org_id,
                    "salbar": salbar_id
                }
                queryset = self.queryset.get(pk=pk)
                serializer = self.serializer_class(instance=queryset, data=request.data)

                serializer = BankAccountRequestSerializer(data=bank_request_body)
                if not serializer.is_valid():
                    return request.send_error_valid(serializer.errors)

                serializer.save()
                return request.send_rsp("INF_013", '')

    @login_required()
    def delete(self, request, pk=None):
        """ Дансны  мэдээлэл устгах"""
        account_body = dict()
        qs = self.queryset.filter(pk=pk).first()

        if not request.employee or request.employee.is_hr and qs:
            self.destroy(request)
            return request.send_rsp("INF_003", '')
        elif qs:
            org_id, sub_org_id, salbar_id = self.set_orgs_and_more(request)

            bank_request_body = {
                "bank": qs.bank.id,
                "number": qs.number,
                "employee": request.employee.id,
                "state": BankAccountRequest.DELETE,
                "bank_account": qs.id,
                "org": org_id,
                "sub_org": sub_org_id,
                "salbar": salbar_id
            }

            serializer = BankAccountRequestSerializer(data=bank_request_body)
            if not serializer.is_valid():
                return request.send_error_valid(serializer.errors)

            serializer.save()
            return request.send_rsp("INF_013", '')


class BankAccountInfoListApiView(APIView):
    """ Нэвтэрсэн хэрэглэгчтэй холбоотой банкны дансны жагсаалт"""

    @login_required()
    def get(self, request, pk=None):

        banks_info = BankAccountInfo.objects.filter(user=pk if pk else request.user.id).order_by("updated_at")

        serializer = BankAccountInfoSerializer(banks_info, many=True)
        return request.send_data(serializer.data)


class BankAccountPaginationApiView(APIView):

    @login_required()
    def get(self, request, pk=None):
        query = BankAccountRequest.objects\
            .filter(
                (Q(**request.exactly_org_filter) & Q(employee__user__userinfo__action_status=UserInfo.APPROVED)) & \
                ( Q(state=BankAccountRequest.DELETE) | Q(state=BankAccountRequest.CREATE) | Q(state=BankAccountRequest.UPDATE))
            )\
            .annotate(
                state_display=WithChoices(BankAccountRequest.STATE_TYPE, 'state'),
                full_name=F("employee__user__userinfo__first_name"),
                bank_name=F("bank__name"),
            )

        paginated = data_table(query, request)
        paginated['data'] = BankAccountRequestSerializer(paginated['data'], many = True).data
        return Response(paginated)


class BankAccountRequestActionApiView(APIView):

    """ Банкны мэдээлэл өөрчлөх,үүсгэх,устгах хүсэлт шийдвэрлэх нь """
    @login_required()
    @has_permission(must_permissions=['userinfo-request-action'])
    def put(self, request):
        # Тухайн хүсэлт байх бол хүсэлтийн мэдээлэл алдаатай байна гэж үзнэ
        change_request = BankAccountRequest.objects.filter(pk=request.data.get('id')).first()
        if not change_request:
            return request.send_error("ERR_013")

        # Тухайн хүсэлтэнд хүний нөөцийн төлөв байхгүй бол хүсэлтийг алдаатай байна гэж үзнэ
        if 'action_status' not in request.data:
            return request.send_error("ERR_013")

        # Хүсэлтийн төрөл нь delete байх юм бол
        if request.data['state'] == str(BankAccountRequest.DELETE):

            account_info = BankAccountInfo.objects.filter(pk=request.data.get('bank_account')).first()

            # Тухайн дансны бүртгэл байхгүй бол хүсэлтийг цуцлан алдаа буцаана
            if not account_info:
                change_request.state=BankAccountRequest.DECLINED
                change_request.save()
                return request.send_error("ERR_013")

            # Хүний нөөц зөвшөөрсөн бол тухайн дансыг устгана
            if request.data['action_status'] == BankAccountRequest.APPROVED:
                account_info.delete()
                change_request.bank_account=None
                change_request.state=BankAccountRequest.APPROVED
                change_request.save()
            # Цуцалсан бол хүсэлтийг цуцалсан төлөвт шилжүүлнэ
            else:
                change_request.state=BankAccountRequest.DECLINED
                change_request.save()

        # Хүсэлтийн төрөл нь create байх юм бол
        elif request.data['state'] == str(BankAccountRequest.CREATE):
            # Хүний нөөц зөвшөөрсөн бол тухайн дансыг үүсгэнэ
            if request.data['action_status'] == BankAccountRequest.APPROVED:
                # Хүсэлт гаргагчийн дансны дугаар бүртгэлтэй байвал сануулга буцаагд хүсэлтийг цуцлана
                check = BankAccountInfo.objects.filter(number=request.data['number'])
                if check:
                    change_request.state=BankAccountRequest.APPROVED
                    change_request.save()
                    return request.send_warning("WRN_009", [], "данс")

                account_body = dict()
                employee = Employee.objects.filter(pk=request.data['employee']).first()
                account_body = {
                    "bank": request.data['bank'],
                    "number": request.data['number'],
                    "user": employee.user.id,
                }

                serializer = BankAccountInfoSerializer(data=account_body)
                if not serializer.is_valid():
                    return request.send_error_valid(serializer.errors)

                bank_account = serializer.save()

                change_request.bank_account=bank_account
                change_request.state=BankAccountRequest.APPROVED
                change_request.save()
            # Цуцалсан бол хүсэлтийг цуцалсан төлөвт шилжүүлнэ
            else:
                change_request.state=BankAccountRequest.DECLINED
                change_request.save()

        # Хүсэлтийн төрөл нь update байх юм бол
        elif request.data['state'] == str(BankAccountRequest.UPDATE):
            if request.data['action_status'] == BankAccountRequest.APPROVED:
                # Хүсэлт гаргагчийн дансны дугаар бүртгэлтэй байвал сануулга буцаагд хүсэлтийг цуцлана
                check = BankAccountInfo.objects.filter(number=request.data['number'])
                if check:
                    change_request.state=BankAccountRequest.APPROVED
                    change_request.save()
                    return request.send_warning("WRN_009", [], "данс")

                account_body = dict()
                employee = Employee.objects.filter(pk=request.data['employee']).first()
                account_body = {
                    "bank": request.data['bank'],
                    "number": request.data['number'],
                    "user": employee.user.id,
                }

                queryset = BankAccountInfo.objects.get(pk=request.data['bank_account'])
                serializer = BankAccountInfoSerializer(instance=queryset, data=account_body)

                if not serializer.is_valid():
                    return request.send_error_valid(serializer.errors)

                bank_account = serializer.save()

                change_request.bank_account=bank_account
                change_request.state=BankAccountRequest.APPROVED
                change_request.save()
            # Цуцалсан бол хүсэлтийг цуцалсан төлөвт шилжүүлнэ
            else:
                change_request.state=BankAccountRequest.DECLINED
                change_request.save()
        else:
            return request.send_error("ERR_013")

        return request.send_info("INF_002")
