from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_delete

from main.utils.user_percent import CalcUserPercent


def delete_progress_signal(Model):

    @receiver(post_delete, sender=Model)
    def decrement_category_usage(sender, instance, **kwargs):

        model_name = Model.__name__
        if model_name in ['UserEducationInfo', 'UserEducationDoctor']:
            user_id = instance.user_education.user_id
        else:
            user_id = instance.user_id

        CalcUserPercent(
            user_id=user_id,
            model_name=model_name
        ).calc()
