from rest_framework.response import Response

from main.utils.rsp.cException import CException
from main.utils.rsp.info import info
from main.utils.rsp.errors import errors
from main.utils.rsp.warnings import warnings
from main.utils.message import send_message


def success_fn(get_response):
    ''' Амжилттай болсон return хийх нэг бүтэц
    '''

    def _send_data(data, status=200):
        '''
            Амжилттай болсон success датаг буцаах нь
            Parameters:
            * data: any
                Мэдээлэлтэй хамт буцаах дата
        '''

        return Response(
            {
                "success": True,
                "data": data,
                "error": "",
            },
            status=status
        )


    def _send_info(info_code, *args):
        '''
            Амжилттай болсон success мэдээллийг буцаах нь

            Parameters:
            * ``info_code``: ``str``
                Info мэдээллийн code нь
            * args: str
                info ний мэдээлэлд оноож өгөх үгнүүд
        '''

        #   message дээр argument ээр ирсэн үгийг оноож өгөх нь
        info[info_code]['message'] = info[info_code]['message'].format(*args)
        status_code = info[info_code]['status_code'] or 201

        return Response(
            {
                "success": True,
                "error": "",
                "info": info[info_code]
            },
            status=status_code
        )


    def _send_rsp(info_code, data, *args):
        '''
            Амжилттай болсон success мэдээллийг датаны хамт буцаах нь
            Parameters:
            * info_code: str
                Info мэдээллийн code нь
            * data: any
                Мэдээлэлтэй хамт буцаах дата
            * args: str
                info ний мэдээлэлд оноож өгөх үгнүүд
        '''

        #   message дээр argument ээр ирсэн үгийг оноож өгөх нь
        info[info_code]['message'] = info[info_code]['message'].format(*args)
        status_code = info[info_code]['status_code'] or 201

        return Response(
            {
                "success": True,
                "data": data,
                "error": "",
                "info": info[info_code],
            },
            status=status_code
        )


    def _send_error(error_code, *args):
        ''' Алдааны мэссэжийг ажиллуулах

            * ``error_code - str`` Алдааны код
            * ``args - obj`` Динамик агуулгыг буцаах
        '''
        return CException(error_code, *args)

    def _send_error_valid(errors):
        '''
            serializer ийн errors ийг буцаана
        '''
        return Response(
            {
                "success": False,
                "data": [],
                "error": "",
                "errors": errors
            },
            status=400
        )

    def _send_warning(warning_code, data=[], *args):
        """
            Анхааруулгыг буцаана
        """

        #   message дээр argument ээр ирсэн үгийг оноож өгөх нь
        warning_obj = { **warnings[warning_code] }
        warning_obj['message'] = f"Анхааруулга {warning_obj['code']}: {warning_obj['message'].format(*args)}"
        status_code = warning_obj['status_code'] or 201

        return Response(
            {
                "success": False,
                "data": data,
                "error": "",
                "errors": [],
                'warning': warning_obj
            },
            status=status_code
        )

    def middleware(request):

        def _send_message(type, code, *args):
            """ Front руугаа message явуулах нь
                type = message ний төрөл
                message = message ний үг
            """

            prefix = "Мэдээлэл"
            rsp = info
            if code.startswith("ERR"):
                prefix = "Алдаа"
                rsp = errors

            message = rsp[code]['message'].format(*args)
            message_code = rsp[code]['code']
            send_message(request, type, f"{prefix} {message_code}: {message}")

        #  view үүд рүү очих request дотор response буцаах функцийг оноосон нь
        request.send_data = _send_data
        request.send_info = _send_info
        request.send_rsp = _send_rsp
        request.send_error = _send_error
        request.send_message = _send_message
        request.send_error_valid = _send_error_valid
        request.send_warning = _send_warning

        response = get_response(request)
        return response

    return middleware
