from celery import shared_task
from templated_email import send_templated_mail
from .models import User


@shared_task(name='accounts.send_mail')
def send_mail(user_id, template_name, scheme, host):
    user = User.objects.get(id=user_id)
    send_templated_mail(
        template_prefix='accounts/',
        template_name=template_name,
        template_suffix='.html',
        from_email='horoomy2017@gmail.com',
        recipient_list=[user.email],
        fail_silently=True,
        context={
            'name': user.name,
            'host': host,
            'scheme': scheme,
            'key': user.vn_key,
        }
    )
