import mimetypes
import math
import os
import shutil
import pathlib

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.urls import reverse

def file_exists(path: str):
    """ Тухайн нэг файлаа эсэхийг шалгах нь
        path: файлын зам
    """
    exists = os.path.isfile(path)
    return exists


def join_media_root(path: str):
    """ Тухайн зам дээр media ийн замыг залгах нь
        path: файлын зам
    """

    return os.path.join(settings.MEDIA_ROOT, path)


def copy_file(original, target):
    """ Тухайн файлыг өөр зам руу хуулах """
    path = shutil.copyfile(original, target)
    return path


def duplicate(file):
    new_file = ContentFile(file.read(), name=file.name)
    return new_file


def open_file(path):
    with open(path, 'rb') as f:
        contents = f.read()
    return contents


def clone(path):
    """ Тухайн файлыг хуулбарлах нь """
    fs = FileSystemStorage()
    new_path = fs.save(path, ContentFile(open_file(path)))
    return new_path


def remove_file(path):
    """ Файлыг устгах нь """
    if file_exists(path):
        os.remove(path)
        return True
    else:
        return False


def get_name_from_path(path):
    """ Замнаас файлын нэрийг авах нь """
    return os.path.basename(path)


def get_extension(path):
    """ Замнаас файлын төрлийг авах нь """
    return pathlib.Path(path).suffixes


def calc_size(size: int):
    sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    if size == 0:
        return ""
    i = math.floor(math.log(size) / math.log(1024))
    if i == 0:
        return f'{size} {sizes[i]}'
    return '{:.2f} {}'.format((size / (1024 ** i)), sizes[i])


def get_content_type(path):
    """ замнаас нь файлын content_type г авах нь
        ex: test.pdf --> appliaction/pdf
    """
    return mimetypes.guess_type(path)


def get_attachment_url(attach_id):
    """ attachment ийн id г үүсгэж авах нь """
    return reverse("attachment", args=(attach_id, ))


def get_file_field_exists(file_field):
    if file_field:
        return file_field.storage.exists(file_field.name)
    else:
        return False
