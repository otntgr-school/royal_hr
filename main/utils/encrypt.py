import base64
from django.conf import settings

from cryptography.fernet import Fernet

def encrypt(txt):
    # convert integer etc to string first
    txt = str(txt)
    # get the key from settings
    cipher_suite = Fernet(settings.ENCRYPT_KEY) # key should be byte
    # #input should be byte, so convert the text to byte
    encrypted_text = cipher_suite.encrypt(txt.encode('ascii'))
    # encode to urlsafe base64 format
    encrypted_text = base64.urlsafe_b64encode(encrypted_text).decode("ascii")
    return encrypted_text


def decrypt(txt):
    # base64 decode
    txt = base64.urlsafe_b64decode(txt)
    cipher_suite = Fernet(settings.ENCRYPT_KEY)
    decoded_text = cipher_suite.decrypt(txt).decode("ascii")
    return decoded_text
