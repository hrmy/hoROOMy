from django.shortcuts import render
from .forms import *
from .models import *
from django.conf import settings
from django.http import Http404
from django.http import HttpResponse, FileResponse
from django.contrib.auth.decorators import login_required
import os
from .tasks import send_mail


@login_required
def document_upload(request):
    if request.method == 'POST':
        form = DocumentSendForm(request.POST, request.FILES)
        if form.is_valid():
            instance = Document(document=request.FILES['document'])
            instance.comment = form.cleaned_data.get('comment')
            instance.user = request.user
            instance.save()
            send_mail.delay(instance.id, 'document_sent_mail', request.scheme, request.get_host())
            return render(request, 'documents/document_sent.html', locals())
    else:
        form = DocumentSendForm()
    return render(request, 'documents/document_send.html', locals())


@login_required
def documents_list(request):
    documents = Document.objects.all()
    return render(request, 'documents/documents_list.html', locals())


@login_required
def document_download(request, id):
    document = Document.objects.get(id=id)
    file_path = os.path.join(settings.MEDIA_ROOT, str(document.document))
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404


@login_required
def document(request, id):
    document = Document.objects.get(id=id)
    is_pdf = False
    if document.file_extension == 'pdf':
        is_pdf = True
    if request.method == 'POST':
        general_form = ContractForm(request.POST)
        if general_form.is_valid():
            cd = general_form.cleaned_data
            #Renter
            renter = Renter()
            renter.first_name = cd.get('renter_first_name')
            renter.second_name = cd.get('renter_second_name')
            renter.patronymic = cd.get('renter_patronymic')
            renter.passport_series = cd.get('renter_passport_series')
            renter.passport_number = cd.get('renter_passport_number')
            renter.save()
            #Landlord
            landlord = Landlord()
            landlord.first_name = cd.get('landlord_first_name')
            landlord.second_name = cd.get('landlord_second_name')
            landlord.patronymic = cd.get('landlord_patronymic')
            landlord.passport_series = cd.get('landlord_passport_series')
            landlord.passport_number = cd.get('landlord_passport_number')
            landlord.save()
            #Contract
            contract = Contract()
            contract.type = cd.get('type')
            contract.renter = renter
            contract.landlord = landlord
            contract.document = document
            contract.save()

            return render(request, 'documents/contract_registered.html', locals())

    else:
        general_form = ContractForm()

    return  render(request, 'documents/document.html', locals())

@login_required
def document_open(request, id):
    document = Document.objects.get(id=id)
    if document.file_extension != 'pdf':
        raise Http404
    file_path = os.path.join(settings.MEDIA_ROOT, str(document.document))
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404
