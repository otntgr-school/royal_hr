from datetime import date
from django.apps import apps

def calculate_birthday(register):
    gender = ''
    try:
        # РД-аас төрсөн өдөр бодох
        if register[4] in ['2', '3']:
            year = int('20' + register[2:4])
            month = int(register[4:6]) - 20
        else:
            year = int('19' + register[2:4])
            month = int(register[4:6])
        day = int(register[6:8])
        # РД-аас хүйс бодох
        UserInfo = apps.get_model("core", 'UserInfo')
        last_number = int(register[-2])
        if (last_number % 2) == 0:
            gender = UserInfo.GENDER_FEMALE
        else:
            gender = UserInfo.GENDER_MALE

        return date(year, month, day), gender

    except:
        return None, gender
