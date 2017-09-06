from django.shortcuts import render
from django.views.generic import TemplateView
from django.utils import timezone

from fanart.models import Contest


class HomeView(TemplateView):
    template_name = 'fanart/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        context['current_contest'] = Contest.objects.filter(type='global', is_active=True, date_start__lt=timezone.now()).order_by('-date_created').first()

#SELECT *,DATEDIFF(deadline,NOW()) AS days_left FROM contests
#WHERE type='global'
#AND active=1
#AND startdate<NOW()
#ORDER BY created DESC
#LIMIT 1

        return context

