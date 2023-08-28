import colorama
from colorama import Fore, Back

colorama.init(autoreset=True)


def color_print(get_response):
    # One-time configuration and initialization.

    print(Fore.BLACK + Back.CYAN + "TERMINAL дээр өнгө ашиглаж болохоор боллоо")

    def middleware(request):

        response = get_response(request)

        return response

    return middleware
