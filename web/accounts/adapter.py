from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from .models import SocialNetworks
from django.core.urlresolvers import reverse_lazy

class UserSocialAccountAdapter(DefaultSocialAccountAdapter):


    def save_user(self, request, sociallogin, form=None):
        data = sociallogin.account.extra_data

        provider = sociallogin.account.provider


        if provider == 'vk':
            name = data['first_name']
            second_name = data['last_name']
        elif provider == 'google':
            name = data['given_name']
            second_name = data['family_name']

        user = sociallogin.user
        user.name = name
        user.second_name = second_name
        user.email = data.get('email')
        user.save()
        sn = SocialNetworks.objects.create()
        if provider == 'vk':
            sn.vk = 'https://vk.com/id' + str(data['uid'])
        elif provider == 'google':
            sn.go = 'https://plus.google.com/' + str(data['id']) + '?hl=ru'
        sn.user = user
        sn.save()


class UserAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        return reverse_lazy('creditals')