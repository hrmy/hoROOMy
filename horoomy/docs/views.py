from easy_pdf.rendering import render_to_pdf_response
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.utils.timezone import now
from .forms import *
from horoomy.parsers.models import *


@login_required
def generate(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)
    if request.method == 'POST':
        initials_form = InitialsForm(request.POST)
        passport_form = PassportForm(request.POST)
        rent_form = RentForm(request.POST)
        if all(i.is_valid() for i in (initials_form, passport_form, rent_form)):
            passport = passport_form.cleaned_data
            rent = rent_form.cleaned_data
            return render_to_pdf_response(
                request=request,
                template='docs/pdf.html',
                context=get_pdf_context(locals())
            )
        else:
            messages.error(request, 'Error')
    else:
        initial = {'name': request.user.name, 'second_name': request.user.second_name}
        initials_form = InitialsForm(initial=initial)
        passport_form = PassportForm()
        rent_form = RentForm()
    return render(request, 'docs/generate.html', locals())


def get_pdf_context(context):
    DATE = now().strftime('%d / %m / %Y') + ' г.'
    OWNER_FULL_NAME = context['ad'].contacts.name or '[???]'
    RENTER_FULL_NAME = context['initials_form'].get_full_name()
    TYPE = Flat.TYPE_CHOICES[context['ad'].flat.type]
    ROOMS = context['ad'].flat.rooms
    ADDRESS = context['ad'].flat.location.address or '[???]'
    START_DATE = context['rent']['start'].strftime('%d / %m / %Y') + ' г.'
    END_DATE = context['rent']['end'].strftime('%d / %m / %Y') + ' г.'
    COST_RUB = context['ad'].flat.cost
    COST_USD = COST_RUB // 60
    DEPOSIT_RUB = context['rent']['deposit']
    RENTER_PASS_SERIES = context['passport']['series']
    RENTER_PASS_NUMBER = context['passport']['number']
    RENTER_PASS_MADE_BY = context['passport']['made_by']
    RENTER_PASS_ADDRESS = context['passport']['address']
    return locals()