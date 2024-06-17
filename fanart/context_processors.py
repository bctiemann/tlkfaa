from django.conf import settings

def settings_constants(request):

    context = {
        'admin_name': settings.ADMIN_NAME,
        'admin_email': settings.ADMIN_EMAIL,
        '30th_anniversary': settings.ANNIVERSARY_30,
    }
    return context
