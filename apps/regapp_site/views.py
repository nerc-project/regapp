
from django.shortcuts import render
import re
import json


def index(request):
    return render(request, 'regapp_site/index.j2', {})


def claims(request):
    print(request.META)
    context = {
        'headers': request.META,
        'userinfo': request.oidc_userinfo
    }
    return render(request, 'regapp_site/claims.j2', context)


def claimsx(request):
    regex = re.compile('^HTTP_')

    oidcinfo = dict((regex.sub('', header), value) for (header, value)
                              in request.META.items() if header.startswith('HTTP_OIDC'))

    userinfo = json.loads(oidcinfo['OIDC_USERINFO_JSON'])

    # Each group provides a list of zero or more key instances in each
    # category.
    # Each category has contributions from zero or more groups
    # Possible categroy contents: 
    # [] - no groups have category
    # [{},{}...{}] - only one group has category
    # [[{},{}...{}],[{},{}...{}],...[{},{}...{}]] - multiple groups have category
    allkeys = {}
    for category in ['RGW_RO_KEYINFO', 'RGW_DMGR_KEYINFO', 'RBD_DMGR_KEYINFO']:
        catkeys = []
        for k in userinfo.get(category, []):
            catkeys.extend(k) if type(k) is list else catkeys.append(k)
        allkeys[category] = catkeys

    print(allkeys)

    # fetch_cilogon(oidcinfo['OIDC_ACCESS_TOKEN'])    
    # fetch_users()

    context = {'headers': oidcinfo, 'userinfo': userinfo}
    context['headers']['REMOTE_USER'] = request.META['REMOTE_USER']
    return render(request, 'nesesite/claims.j2', context)