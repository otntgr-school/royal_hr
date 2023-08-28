from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import mixins
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from core.models import SubOrgs
from core.models import Orgs

from .serializer import SubOrgsSerializer
from .serializer import OrgsJsonSerializer
from .serializer import OrgsSerializer
from .serializer import SubOrgsCRSerializer

from main.utils.datatable import data_table
from main.decorators import login_required
from main.decorators import has_permission


class SubCompanyRegisterJsonApiView(APIView):

    @login_required()
    def get(self, request):
        ''' Энэ нь orgs болон suborgs-ийн jstree-гийн утгыг авах функц
        '''
        # Бүх утгаа баазаас авч serializer дээр өөрчлөлтүүд хийж байна
        orgsData = Orgs.objects.filter(id=request.org_filter.get("org").id)
        serialized_data = OrgsJsonSerializer(orgsData, many=True, context={ "request": request }).data

        # json файл буцаана
        return Response(serialized_data)


class UserListTableJsonApiView(APIView):

    def get(self, request):
        ''' Worker list-ийн datatable-ийн утгыг авна
        '''
        qs = Orgs.objects.filter()
        paginated = data_table(qs, request)
        paginated['data'] = OrgsSerializer(paginated['data'], many=True).data
        return Response(paginated)


class SubCompanyRegisterAPIView(APIView):
    ''' Дэд байгууллага CRUD үйлдэл
    '''

    serializer_class = SubOrgsSerializer
    queryset = SubOrgs.objects

    crud_serializer = SubOrgsCRSerializer

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/sub-org/index.html'

    @login_required()
    @has_permission(must_permissions=['sub-company-read'])
    def get(self, request, pk=None):

        if pk:
            queryset = self.queryset.get(pk=pk)
            serializer = self.serializer_class(instance=queryset)
            return Response(
            {
                'serializer': serializer,
                'data': queryset,
                'pk': pk
            })

        return Response(
        {
            'serializer': self.serializer_class,
        })

    # post
    @login_required()
    @has_permission(allowed_permissions=['sub-company-create','sub-company-update'])
    def post(self, request, pk=None):
        """ шинээр үүсгэх нь:
        - ``name`` - Нэр
        - ``org`` - Байгууллага ID
        """

        request.data._mutable = True
        request.data['org'] = request.org_filter.get("org").id
        request.data._mutable = False

        if pk:
            if not request.data['logo']:
                request.data._mutable = True
                request.data.pop('logo')
                request.data._mutable = False

            queryset = self.queryset.get(pk=pk)
            serializer = self.serializer_class(instance=queryset, data=request.data)

            if not serializer.is_valid():
                request.send_message("error", "ERR_001")
                return Response(
                    {
                        'serializer': self.serializer_class,
                        'pk': pk
                    }
                )

            # Өмнөх зураг байгаа эсэхийг шалгаад устгах
            try:
                request.data['logo']
                if queryset.logo:
                    queryset.logo.delete()
            except:
                None

        else:
            serializer = self.crud_serializer(data=request.data)

            if not serializer.is_valid():
                request.send_message("error", "ERR_001")
                return Response(
                    {
                        'serializer': self.serializer_class,
                    }
                )

        serializer.save()
        return redirect("sub-company-register")

class SubOrgDeleteApiView(APIView):

    @login_required()
    @has_permission(must_permissions=['sub-company-delete'])
    def get(self, request, pk):

        SubOrgs.objects.filter(pk=pk).delete()
        request.send_message("success", "INF_003")
        return redirect('sub-company-register')
