from django.contrib import messages

def send_message(request, type, message):
    """ Front руугаа message явуулах нь
        type = message ний төрөл
        message = message ний үг
    """
    types = {
        "success": messages.success,
        'error': messages.error,
        'warning': messages.warning,
        'info': messages.info,
        'debug': messages.debug,
    }

    message_fn = types.get(type)
    message_fn(request, message)
