from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer

from core.models import FAQ
from core.models import FAQGroup

from .serializer import FAQGroupPageSerializer
from .serializer import FAQListSerializer
from .serializer import FAQSerializer
from .serializer import FAQuestionPaginateSerializer
from .serializer import FAQuestionSerializer

from main.utils.datatable import data_table

class FAQPageApiView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/FAQ/index.html'
    def get(self, request):
        return Response({})


class FAQHTMLApiView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/FAQ/CreateGroup/index.html'
    def get(self, request):
        return Response({})


class FAQActionApiView(APIView):
    def post(self, request, pk=None):
        serilaizer = FAQSerializer(data=request.data)

        if serilaizer.is_valid():
            serilaizer.save()
            return request.send_info("INF_001")

        return request.send_error_valid(serilaizer.errors)

    def get(self, request, pk):
        obj = FAQGroup.objects.get(pk=pk)
        serializer = FAQSerializer(instance=obj).data
        return request.send_data(serializer)

    def put(self, request, pk):
        obj = FAQGroup.objects.get(pk=pk)
        serializer = FAQSerializer(instance=obj, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return request.send_info("INF_002")

        return request.send_error_valid(serializer.errors)

    def delete(self, request, pk):
        obj = FAQGroup.objects.get(pk=pk)
        obj.delete()
        return request.send_info("INF_003")


class FAQGroupPaginate(APIView):
    def get(self, request, pk=None):
        qs = FAQGroup.objects.all()
        paginated = data_table(qs, request)
        paginated['data'] = FAQGroupPageSerializer(paginated['data'], many = True).data
        return Response(paginated)


class FAQuestionHTMLApiView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/FAQ/CreateQA/index.html'

    def get(self, request):
        qs = FAQGroup.objects.all()
        serializer = FAQSerializer(instance=qs, many=True).data
        return Response({'faqgroup': serializer})


class FAQuestionActionApiView(APIView):
    def post(self, request, pk=None):
        serilaizer = FAQuestionSerializer(data=request.data)

        if serilaizer.is_valid():
            serilaizer.save()
            return request.send_info("INF_001")

        return request.send_error_valid(serilaizer.errors)

    def get(self, request, pk):
        obj = FAQ.objects.get(pk=pk)
        serializer = FAQuestionSerializer(instance=obj).data
        return request.send_data(serializer)

    def put(self, request, pk):
        obj = FAQ.objects.get(pk=pk)
        serializer = FAQuestionSerializer(instance=obj, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return request.send_info("INF_002")

        return request.send_error_valid(serializer.errors)

    def delete(self, request, pk):
        obj = FAQ.objects.get(pk=pk)
        obj.delete()
        return request.send_info("INF_003")


class FAQuestionPaginate(APIView):
    def get(self, request, pk=None):
        group_id = request.GET.get("groupId")
        if group_id:
            qs = FAQ.objects.filter(group_id=group_id)
        else:
            qs = FAQ.objects.all()
        paginated = data_table(qs, request)
        paginated['data'] = FAQuestionPaginateSerializer(paginated['data'], many = True).data
        return Response(paginated)


class FAQListApi(APIView):
    def get(self, request):
        if request.user.is_employee:
            qs = FAQGroup.objects.all()
        else:
            qs = FAQGroup.objects.filter(type=FAQGroup.NOT_WORKER)
        serialzier = FAQListSerializer(instance=qs, many=True).data
        return request.send_data(serialzier)
