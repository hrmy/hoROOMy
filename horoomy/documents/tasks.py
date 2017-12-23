from celery import shared_task
from templated_email import send_templated_mail


@shared_task(name='accounts.send_mail')
def send_mail(document_id, template_name, scheme, host):
    send_templated_mail(
        template_prefix='documents/',
        template_name=template_name,
        template_suffix='.html',
        from_email='horoomy2017@gmail.com',
        recipient_list=['horoomy2017@gmail.com'],
        fail_silently=True,
        context={
            'document_id': document_id,
            'host': host,
            'scheme': scheme,
        }
    )
