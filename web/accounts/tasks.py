from __future__ import absolute_import, unicode_literals

from celery import shared_task
from templated_email import send_templated_mail
from .models import User
from datetime import timedelta
from django.utils import timezone



@shared_task
def send_mail(user_id, template_name, scheme, host):
    print(user_id, template_name, scheme, host)
    user = User.objects.get(id=user_id)

    mail_sent = send_templated_mail(
        template_prefix='accounts/',
        template_name=template_name,
        template_suffix='html',
        from_email='horoomy2017@gmail.com',
        recipient_list=[user.email],
        context={
            'name': user.name,
            'host': host,
            'scheme': scheme,
            'key': user.vn_key,
        }
    )

    return mail_sent

@shared_task
def clean_users():
    users = User.objects.filter(is_active=False).filter(vn_expire__gte=timezone.now()).delete()
