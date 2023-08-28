import json
import os
import datetime
import openpyxl

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db.models import Q

from rest_framework.views import APIView

from core.models import WorkingTimeSchedule
from core.models import TimeScheduleRegister
from core.models import WorkingTimeScheduleType
from core.models import XyTimeScheduleValues
from core.models import RequestTimeVacationRegister
from core.models import Employee
from core.models import HolidayDayInYear

# Одоогийн цаг
now_time = datetime.datetime.now()


def employee_register_time(request, employee_id, date_time_record):

    today = datetime.datetime.today()
    formatted_time = datetime.datetime.strptime(date_time_record, "%m/%d/%Y %I:%M:%S %p")
    formatted_date = formatted_time.date()

    # Торгууль
    fine = 0
    hotsorson_time = ''

    # Цагийн хуваарийн төрөлд бүртгүүлээгүй бол нүүр хуудас луу буцаана
    qs_working_time_sch = WorkingTimeSchedule.objects.filter(employees__register_code=employee_id).last()

    if not qs_working_time_sch:
        return False, "ERR_016"

    time_register = TimeScheduleRegister.objects.filter(employee__register_code=employee_id, date=formatted_date).last()

    # Аль хэдийн цагаа явуулзан бол дахиж уншихгүй (7 хоног )
    if  (
            int(qs_working_time_sch.type.code) == WorkingTimeScheduleType.TYPE_CODE.get('seven_days') and

            time_register and

            time_register.in_dt and
            time_register.out_dt and
            time_register.lunch_in_dt and
            time_register.lunch_out_dt
        ):

        return True, "ERR_018"

    # Цайндаа орох үеийн цагйиг хадгалах ( 7 хоног )
    if  (
            time_register and

            time_register.in_dt and
            not time_register.out_dt and
            not time_register.lunch_in_dt and
            not time_register.lunch_out_dt and

            time_register.in_dt != formatted_time and
            (formatted_time - time_register.in_dt) > datetime.timedelta(minutes=3) and

            int(qs_working_time_sch.type.code) == WorkingTimeScheduleType.TYPE_CODE.get('seven_days')
        ):

        time_register.lunch_in_dt = formatted_time
        time_register.lunch_out_dt = formatted_time  # muis 1 l dardag bolhor shuud hadgalchihaj bga ym
        time_register.save()

        return True, "INF_015"

    # # Цайнаас ирэх үеийн цагйиг хадгалах ( 7 хоног )
    # if  (
    #         time_register and

    #         time_register.in_dt and
    #         not time_register.out_dt and
    #         time_register.lunch_in_dt and
    #         not time_register.lunch_out_dt and

    #         time_register.in_dt != formatted_time and
    #         (formatted_time - time_register.lunch_in_dt) > datetime.timedelta(minutes=3) and

    #         int(qs_working_time_sch.type.code) == WorkingTimeScheduleType.TYPE_CODE.get('seven_days')
    #     ):

    #     time_register.lunch_out_dt = formatted_time
    #     time_register.save()

    #     return True, "INF_015"

    # Явсан цагаа явуулж байвал ( 7 хоног )
    if  (
            time_register and

            time_register.in_dt and
            not time_register.out_dt and
            time_register.lunch_in_dt and
            time_register.lunch_out_dt and

            time_register.in_dt != formatted_time and
            (formatted_time - time_register.lunch_out_dt) > datetime.timedelta(minutes=3) and

            int(qs_working_time_sch.type.code) == WorkingTimeScheduleType.TYPE_CODE.get('seven_days')
        ):

        value = formatted_time - time_register.in_dt - (time_register.lunch_out_dt - time_register.lunch_in_dt)

        # Хэдэн цаг ажилссаныг тооцох (Нийт хэдэн сек олоод хувиргаад олно)
        s = int(value.total_seconds())
        hours = s // 3600
        s = s - (hours * 3600)
        minutes = s // 60
        seconds = s - (minutes * 60)
        worked_time = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

        time_register.worked_time = str(worked_time)
        time_register.out_dt = formatted_time
        time_register.save()

        return True, "INF_015"

    # Явсан цагаа явуулж байвал ( XY хоног )
    if  (
            time_register and

            time_register.in_dt and
            not time_register.out_dt and

            time_register.in_dt != formatted_time and
            (formatted_time - time_register.in_dt) > datetime.timedelta(minutes=3) and

            int(qs_working_time_sch.type.code) == WorkingTimeScheduleType.TYPE_CODE.get('xy_days')
        ):

        value = formatted_time - time_register.in_dt

        # Хэдэн цаг ажилссаныг тооцох (Нийт хэдэн сек олоод хувиргаад олно)
        s = int(value.total_seconds())
        hours = s // 3600
        s = s - (hours * 3600)
        minutes = s // 60
        seconds = s - (minutes * 60)
        worked_time = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

        time_register.worked_time = str(worked_time)
        time_register.out_dt = formatted_time
        time_register.save()

        xyTimeScheduleValue = XyTimeScheduleValues.objects.filter(employee__register_code=employee_id).last()

        # Хэрвээ дараачийн ажилж эхлэх цаг нь одоогийн цагаас хэтрээгүй бол шинэчлэхгүй
        if formatted_time > xyTimeScheduleValue.start_next_job_date:

            # Дараачийн ажлын эхлэх цагийг шинэчлэнэ
            start_next_job_date_value = xyTimeScheduleValue.start_next_job_date + relativedelta(hours=qs_working_time_sch.ajillah_time) + relativedelta(hours=qs_working_time_sch.amrah_time)
            xyTimeScheduleValue.start_next_job_date = start_next_job_date_value
            xyTimeScheduleValue.save()

        return True, "INF_015"


    # ---------------- 7 хоногийн Цагийн хуваарийн төрөл ----------------
    if int(qs_working_time_sch.type.code) == WorkingTimeScheduleType.TYPE_CODE.get('seven_days'):

        # Зөвхөн өдрөөр авсаныг шалгаж байна
        today_shaltgaan = RequestTimeVacationRegister.objects.filter(
            Q(start_day=today.date()) & Q(end_day__isnull=False)
        ).first()

        # Өдөрт олон удаа цагаа явуулах гээд spam-даад байвал warning буцаана
        if time_register:

            # Алдаа буцаана
            # 1) Олон удаа spamдуул 2) Амралт, Тасалсан, Олон өдөрүүдээр чөлөө авсан бол
            if (
                time_register.out_dt or
                time_register.kind == TimeScheduleRegister.KIND_AMRALT or
                time_register.kind == TimeScheduleRegister.KIND_TAS or
                time_register.kind == TimeScheduleRegister.KIND_AJILTAI_SHALTGAAN
            ):
                return False, "ERR_017"

            # 1 Өдрөөр хүсэлт авсан бол цаг хамаарахгүй хадгална
            if (time_register.kind == TimeScheduleRegister.KIND_AJILTAI_SHALTGAAN and today_shaltgaan):
                time_register.in_dt = formatted_time
                time_register.save()

                return True, "INF_015"

        # Явсан цаг бүртгэж дуусах хугацаа
        today_time_schedule = formatted_time.strftime('%a').lower() + '_time_schedule'
        # start_time = (getattr(qs_working_time_sch, today_time_schedule)).start_time

        hotorch_boloh_limit = (getattr(qs_working_time_sch, today_time_schedule)).hotorch_boloh_limit

        # # Ажилд ирэх цагаасаа хоцорсон бол торгууль бодно
        # if start_time < formatted_time.time():
        #     fine = fine + qs_working_time_sch.start_time_penalty

        if hotorch_boloh_limit < formatted_time.time():
            hotsorj_irsen_tsag = datetime.datetime.strptime(f'{formatted_time.date()} {hotorch_boloh_limit}', '%Y-%m-%d %H:%M:%S')

            # hotsorson_tsag = datetime.datetime.now() - hotsorj_irsen_tsag
            hotsorson_tsag = formatted_time - hotsorj_irsen_tsag

            # Хэдэн цаг хоцорсныг тооцох
            q = int(hotsorson_tsag.total_seconds())
            hours =q // 3600
            q = q - (hours * 3600)
            minutes = q // 60
            seconds = q - (minutes * 60)
            hotsorson_time = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))


    # --------------- XY хоногийн Цагийн хуваарийн төрөл ----------------
    if int(qs_working_time_sch.type.code) == WorkingTimeScheduleType.TYPE_CODE.get('xy_days'):

        xyTimeScheduleValue = XyTimeScheduleValues.objects.filter(employee__register_code=employee_id).last()

        start_time = xyTimeScheduleValue.start_next_job_date
        hotorch_boloh_limit = qs_working_time_sch.hotorch_boloh_limit

        if hotorch_boloh_limit:
            registration_start_time = start_time + relativedelta(hours=hotorch_boloh_limit.hour, minutes=hotorch_boloh_limit.minute, seconds=hotorch_boloh_limit.second)
        else:
            registration_start_time = start_time

        # # Алдаа буцаана
        # # 1) Амралтын цагаар цагаа явуулах
        # if (today > xyTimeScheduleValue.start_next_vacation_date):
        #     return False, "ERR_018"

        # registration_start_time = xyTimeScheduleValue.start_next_job_date - relativedelta(hours=qs_registration_start_time.hour, minutes=qs_registration_start_time.minute, seconds=qs_registration_start_time.second)
        # start_time = xyTimeScheduleValue.start_next_job_date

        # # Ирсэн цагаа бүртгүүлэх цаг нь одоогийнхоос хэтрээгүй бол цааш явуулахгүй
        # if registration_start_time > formatted_time:
        #     return False, "ERR_018"

        # # Ажилд ирэх цагаасаа хоцорсон бол торгууль бодно
        # if start_time < formatted_time:
        #     fine = fine + qs_working_time_sch.start_time_penalty

        if registration_start_time < formatted_time:
            hotsorson_tsag = datetime.datetime.now() - registration_start_time

            # Хэдэн цаг хоцорсныг тооцох
            w = int(hotsorson_tsag.total_seconds())
            hours = w // 3600
            w = w - (hours * 3600)
            minutes = w // 60
            seconds = w - (minutes * 60)
            hotsorson_time = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))


    # Ирсэн цагийг бүртгэх нь ( 7 хоног )
    if int(qs_working_time_sch.type.code) == WorkingTimeScheduleType.TYPE_CODE.get('seven_days'):
        if not time_register:

            employee_qs = Employee.objects.filter(time_register_employee=employee_id).last()

            qs_holiday = HolidayDayInYear.objects.filter(
                (Q(every_year=True) & Q(date__month=now_time.month) & Q(date__day=now_time.day)) | (Q(every_year=False) & Q(date__year=now_time.year) & Q(date__month=now_time.month) & Q(date__month=now_time.day))
            )

            kind_custom = TimeScheduleRegister.KIND_WORKING

            if qs_holiday:
                kind_custom = TimeScheduleRegister.KIND_AMRALT_AJLIIN

            new_time_register = TimeScheduleRegister(
                employee=employee_qs,
                in_dt=formatted_time,
                date=formatted_date,
                kind=kind_custom,
                fine=fine,
                hotsorson_time=hotsorson_time
            )

            new_time_register.save()
            return True

    # Ирсэн цаг бүртгэх нь ( XY хоног )
    if int(qs_working_time_sch.type.code) == WorkingTimeScheduleType.TYPE_CODE.get('xy_days'):
        time_register_xy = TimeScheduleRegister.objects.filter(employee__register_code=employee_id, out_dt__isnull=False).last()
        if time_register_xy:
            if (formatted_time - time_register_xy.out_dt) > datetime.timedelta(minutes=3):

                employee_qs = Employee.objects.filter(time_register_employee=employee_id).last()

                qs_holiday = HolidayDayInYear.objects.filter(
                    (Q(every_year=True) & Q(date__month=now_time.month) & Q(date__day=now_time.day)) | (Q(every_year=False) & Q(date__year=now_time.year) & Q(date__month=now_time.month) & Q(date__month=now_time.day))
                )

                kind_custom = TimeScheduleRegister.KIND_WORKING

                if qs_holiday:
                    kind_custom = TimeScheduleRegister.KIND_AMRALT_AJLIIN

                new_time_register = TimeScheduleRegister(
                    employee=employee_qs,
                    in_dt=formatted_time,
                    date=formatted_date,
                    kind=kind_custom,
                    fine=fine,
                    hotsorson_time=hotsorson_time
                )

                new_time_register.save()
                return True

    return False


class DeviceRegister(APIView):

    def post(self, request):
        body = request.data

        today = datetime.datetime.today()
        str_today = str(today.date())
        with open(os.path.join(settings.BASE_DIR, 'logs', str_today + ".txt"), 'a') as f:
            f.write(str(today) + ": " + json.dumps(body) + "\n")

        try:
            for data in body:
                employee_register_time(
                    request,
                    employee_id=data['employee_id'],
                    date_time_record=data['date_time_record'],
                )
        except Exception as e:
            with open(os.path.join(settings.BASE_DIR, 'errors', str_today + ".txt"), 'a') as f:
                f.write(f"{str(e)} \n")

        return request.send_data([])



class GetTimeScheduleRegisterDataFromExcel(APIView):

    def post(self, request):

        excel_file = request.FILES.get('file')

        check_date = datetime.datetime.strptime('2022-11-01', "%Y-%m-%d")

        wb = openpyxl.load_workbook(excel_file)

        worksheet = wb["Sheet1"]

        excel_data = list()

        for row in worksheet.iter_rows():
            row_data = dict()
            count = 0

            for cell in row:
                # excel-ийн эхний 2 утгыг л авна
                if count == 2 or cell.value == None:
                    break

                # Employee ID
                if count == 0:
                    row_data['employee_id'] = str(cell.value)
                    count = count + 1
                    continue

                if count == 1:
                    date = datetime.datetime.strptime(str(cell.value), "%Y-%m-%d %H:%M:%S")
                    # date = datetime.datetime.strptime(str(cell.value), "%Y-%m-%d %H:%M:%S") + relativedelta(hours=1)

                    if date < check_date:
                        break

                    date_str = date.strftime('%m/%d/%Y %I:%M:%S %p')
                    row_data['date_time_record'] = str(date_str)
                    count = count + 1
                    break


            if not row_data or not row_data.get('date_time_record') or not row_data.get('employee_id'):
                continue

            # employee_register_time row_data-г шиднэ
            employee_register_time(
                request=request,
                employee_id=row_data.get('employee_id'),
                date_time_record=row_data.get('date_time_record'),
            )
            excel_data.append(row_data)

        return request.send_rsp("INF_001", excel_data)
