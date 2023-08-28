import json
import traceback

from colorama import Fore
from django.http import JsonResponse
from django.shortcuts import redirect

from main.utils.rsp.errors import errors


class ErrorHandlerMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def __get_error_msg(self, request, exception):
        '''
            Exception ий алдааг terminal дээр харуулах нь
        '''
        message = "**{url}**\n\n{error}\n\n````{tb}````".format(
            url=request.build_absolute_uri(),
            error=repr(exception),
            tb=traceback.format_exc()
        )
        return message

    def process_exception(self, request, exception):
        ''' Алдааны мэдээллийг response-оор буцаах функц

        * ``exception``-``str`` Алдааны код болон агуулгыг буцаах
        * ``message``-``str`` Алдааны код
        * ``args``-``str`` Динамик агуулгыг буцаах
        '''
        message = str(exception)
        status_code = 500
        args = None

        try:
            error_dict = json.loads(message)
            message = error_dict['code']
            args = error_dict['args']
        except:
            message = message

        #  response оор алдааны object буцаах үе нь
        error_obj = None
        if message in errors.keys():
            error_obj = {**errors[message]}

            error_obj['message'] = f"Алдаа {error_obj['code']}: {error_obj['message'].format(*args)}"
            status_code = error_obj['status_code'] or status_code
        else:
            error_obj = errors['ERR_004']
            error_msg = self.__get_error_msg(request, exception)
            # expection ий алдааны msg ийг terminal дээр улаан өнгөөр хэвлэх нь
            if "хуудас байхгүй байна." not in error_msg:
                print(Fore.RED + error_msg)

        #  NOTE: ajax хүсэлт байвал json response буцаана
        if hasattr(request, "is_ajax") and request.is_ajax():
            return JsonResponse(
                {
                    "success": False,
                    "data": [],
                    "error": error_obj,
                    "info": {}
                },
                status=status_code
            )
        else:
            request.send_message("error", 'ERR_004')

        if request.META.get('HTTP_REFERER'):
            #  Алдаа гарвал өмнө нь хуудас руу нь илгээх
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            return redirect("home")
