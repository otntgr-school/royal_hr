from django.apps import apps


class CalcUserPercent():

    def __init__(self, user_id, model_name=""):
        self.user_id = user_id
        self.model_name = model_name

        self.max_total = 0
        self.max_has_value = 0
        self.user = None

    @staticmethod
    def display_progress_percent(user=None, user_id=None):

        User = apps.get_model("core", "User")

        user_obj = (
            user
            if user is not None
            else
            User.objects.get(id=user_id)
        )

        hasprogress = hasattr(user_obj, 'userprogress')
        if not hasprogress:
            return 0

        total = 0
        total_value = 0
        for key, value in user_obj.userprogress.progressing.items():
            total += value[0]
            total_value += value[1]

        try:
            return round((total_value * 100) / total, 2)
        except:
            return 0

    def __get_model(self, model_name):
        return apps.get_model('core', model_name)

    def __get_model_fields(self, Model, not_fields):
        return list(filter(lambda x: x.name not in not_fields, Model._meta.fields))

    def __calc_percent(self, obj, fields):

        total = len(fields)
        has_value = 0

        for field in fields:
            value = getattr(obj, field.name)
            if value:
                has_value += 1

        self.max_total += total
        self.max_has_value += has_value

        return total, has_value

    def __get_model_name(self, Model):
        return Model.__name__

    def __check_will_calc(self, Model):
        if not self.model_name:
            return True

        now_model_name = self.__get_model_name(Model)
        return now_model_name == self.model_name

    def __set_progress(self, Model, total, now):
        UserProgress = self.__get_model("UserProgress")
        user = self.user
        has_progress = hasattr(user, 'userprogress')
        progress = None
        if not has_progress:
            progress = UserProgress.objects.create(user=user, progressing={})
        else:
            progress = user.userprogress

        key = self.__get_model_name(Model)

        progress.progressing = {
            **progress.progressing,
            key: [total, now]
        }
        progress.save()

    def __find_obj(self, obj, selector):

        if not selector:
            return obj

        if "." in selector:
            selectors = selector.split(".")
            _obj = obj
            no = False
            for select in selectors:
                if not hasattr(_obj, select):
                    no = True
                    break
                _obj = getattr(_obj, select)

            return (
                _obj
                if not no
                else
                None
            )

        if hasattr(obj, selector):
            return getattr(obj, selector)

        return None

    def __find_percent_with_fields(self, Model, obj, selector, not_fields):
        if not self.__check_will_calc(Model):
            return

        fields = self.__get_model_fields(Model, not_fields)
        _obj = self.__find_obj(obj, selector)
        if not _obj:
            self.__set_progress(Model, len(fields), 0)
            return

        total, has_value = self.__calc_percent(_obj, fields)
        self.__set_progress(Model, total, has_value)

    def __calc_has_one(self, Model, obj, selector):
        if not self.__check_will_calc(Model):
            return

        qs = self.__find_obj(obj, selector)
        if not qs:
            self.__set_progress(Model, 1, 0)
            return

        self.max_total += 1
        is_exists = qs.exists()
        if is_exists:
            self.max_has_value += 1

        self.__set_progress(Model, 1, (1 if is_exists else 0))

    def calc(self, should_save=True):
        User = self.__get_model('User')
        UserInfo = self.__get_model("UserInfo")
        UserEducation = self.__get_model("UserEducation")
        UserEducationInfo = self.__get_model("UserEducationInfo")
        UserEducationDoctor = self.__get_model("UserEducationDoctor")
        UserProfessionInfo = self.__get_model("UserProfessionInfo")
        UserWorkExperience = self.__get_model("UserWorkExperience")
        UserErdmiinTsol = self.__get_model("UserErdmiinTsol")
        UserLanguage = self.__get_model("UserLanguage")
        UserOfficeKnowledge = self.__get_model("UserOfficeKnowledge")
        UserProgrammKnowledge = self.__get_model("UserProgrammKnowledge")
        UserTalent = self.__get_model("UserTalent")
        UserFamilyMember = self.__get_model("UserFamilyMember")
        UserHamaatan = self.__get_model("UserHamaatan")
        UserEmergencyCall = self.__get_model("UserEmergencyCall")
        SkillDefWithUser = self.__get_model("SkillDefWithUser")
        ExtraSkillsDefinations = self.__get_model("ExtraSkillsDefinations")
        UserExperience = self.__get_model("UserExperience")

        user = User.objects.get(id=self.user_id)
        self.user = user
        self.__find_percent_with_fields(
            User,
            user,
            '',
            [
                'mail_verified',
                'id',
                'last_login',
                'is_staff',
                'is_active',
                'password',
                'username',
                'is_superuser',
                'first_name',
                'last_name',
                'info_progress'
            ]
        )

        self.__find_percent_with_fields(
            UserInfo,
            user,
            'info',
            [
                'org',
                'sub_org',
                'salbar',
                'created_at',
                'updated_at',
                'id',
                'user'
            ]
        )

        self.__find_percent_with_fields(
            UserEducation,
            user,
            'usereducation',
            [
                'level',
                'created_at',
                'updated_at',
                'id',
                'user'
            ]
        )

        self.__calc_has_one(
            UserEducationInfo,
            user,
            "usereducation.usereducationinfo_set",
        )

        self.__calc_has_one(
            UserEducationDoctor,
            user,
            "usereducation.usereducationdoctor_set",
        )

        self.__calc_has_one(
            UserProfessionInfo,
            user,
            "userprofessioninfo_set",
        )

        self.__calc_has_one(
            UserWorkExperience,
            user,
            "userworkexperience_set",
        )

        self.__calc_has_one(
            UserErdmiinTsol,
            user,
            "usererdmiintsol_set",
        )

        self.__calc_has_one(
            UserLanguage,
            user,
            "userlanguage_set",
        )

        self.__find_percent_with_fields(
            UserOfficeKnowledge,
            user,
            "userofficeknowledge",
            [
                'id',
                'user'
            ]
        )

        self.__calc_has_one(
            UserProgrammKnowledge,
            user,
            "userprogrammknowledge_set",
        )

        self.__calc_has_one(
            UserTalent,
            user,
            "usertalent_set",
        )

        self.__calc_has_one(
            UserFamilyMember,
            user,
            "userfamilymember_set",
        )

        self.__calc_has_one(
            UserHamaatan,
            user,
            "userhamaatan_set",
        )

        self.__calc_has_one(
            UserEmergencyCall,
            user,
            "useremergencycall_set",
        )

        self.__calc_has_one(
            SkillDefWithUser,
            user,
            "skilldefwithuser_set",
        )

        self.__calc_has_one(
            ExtraSkillsDefinations,
            user,
            "extraskillsdefinations_set",
        )

        self.__calc_has_one(
            UserExperience,
            user,
            "userexperience_set",
        )
