from django.conf import settings

def settings_constants(request):

    context = {
        'admin_name': settings.ADMIN_NAME,
        'admin_email': settings.ADMIN_EMAIL,
    }
    return context
