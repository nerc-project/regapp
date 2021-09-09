from urllib.parse import urlencode
from secrets import token_urlsafe
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse
from django.template.loader import get_template
from ..forms import CreateAccountForm
from ..models import AccountAction


def profile(request):

    nerc_uinfo = request.oidc_userinfo
    data = {
        'first_name': nerc_uinfo.get('given_name', None),
        'last_name': nerc_uinfo.get('family_name', None),
        'username': nerc_uinfo.get('preferred_username', None),
        'email': nerc_uinfo.get('email', None)
    }

    # TODO: Better guard here...
    if request.method != 'GET':
        raise Exception

    # Signal that request was from a form submission
    # Using GET to survive oidc redirect/return pattern.
    if 'email' in request.GET:
        form = CreateAccountForm(request.GET, initial=data)

        if form.is_valid():

            # Rock beats scissors. Kill any extant update
            # for this user.
            AccountAction.objects.filter(sub=nerc_uinfo['sub']).delete()

            pending_update = AccountAction(
                regcode="",
                sub=nerc_uinfo['sub'],
                firstName=form.cleaned_data['first_name'],
                lastName=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                username=form.cleaned_data['username']
            )

            pending_update.save()
        else:
            print(form.errors)

        return redirect('profile_sendupdate')

    else:

        account_form = CreateAccountForm(data)

        account_form.fields['username'].widget.attrs['readonly'] = True

        return render(request, 'profile/index.j2', {
            'form': account_form
        })


def sendupdate(request):
    nerc_uinfo = request.oidc_userinfo

    try:
        pending_update = AccountAction.objects.get(sub=nerc_uinfo['sub'])
        regcode = token_urlsafe(16)
        pending_update.regcode = regcode

        # Check if pending update request is changing email
        if pending_update.email != nerc_uinfo.get('email', None):
            pending_update.opcode = 'update_verify_new_email'
            validation_recipient = nerc_uinfo['email']
            update_with_email_tmpl = get_template(
                "profile/account_update_email.j2"
            )
            msg = update_with_email_tmpl.render({
                "old_email": nerc_uinfo['email'],
                'new_email': pending_update.email,
                'regcode': regcode
            })
        else:
            pending_update.opcode = 'update'
            validation_recipient = pending_update.email
            # TODO: Factor out - used in reapp_site as well...
            update_tmpl = get_template(
                "profile/account_update.j2"
            )
            msg = update_tmpl.render({
                "pending_update": pending_update,
                "regcode": regcode
            })

        pending_update.save()

        send_mail(
            "NERC Account Update Validation",
            msg,
            "support@nerc.mghpcc.org",
            [validation_recipient],
            fail_silently=False
        )

        ctx = {
            'validation_recipient': validation_recipient
        }
    except AccountAction.DoesNotExist as e:
        ctx = {
            'error': e,
            'sub': nerc_uinfo['sub']
        }
        pending_update = None

    return render(request, 'profile/sendupdate.j2', ctx)


def logout(request):
    # clear the django session information

    try:
        del request.session[request.idp]
    except KeyError:
        pass

    # redirect the user to logout of the IdP

    redirect_to_regapp = (
        request.META['HTTP_X_FORWARDED_PROTO'] +
        "://" +
        request.META['HTTP_X_FORWARDED_HOST'] +
        reverse('index')
    )

    redirect_to_keycloak = (
        settings.NERC_LOGOUT_URL +
        "?" +
        urlencode({'redirect_uri': redirect_to_regapp})
    )

    redirect_to_oauth2_proxy = (
        settings.OAUTH2PROXY_NERC_LOGOUT_URL +
        "?" +
        urlencode({'rd': redirect_to_keycloak})
    )

    return redirect(redirect_to_oauth2_proxy)
