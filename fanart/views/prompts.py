import logging

from django.views.generic import ListView, UpdateView
from django.views.generic.edit import FormMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.shortcuts import reverse, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count

from fanart.forms import PromptForm, PromptDeactivateForm
from fanart.response import JSONResponse
from fanart.views import UserPaneMixin
from fanart.models import Prompt, Picture
from fanart.utils import PagesLink

logger = logging.getLogger(__name__)


# Prompts

class PromptsView(UserPaneMixin, FormMixin, ListView):
    template_name = 'fanart/chamber_of_stars/prompts.html'
    model = Prompt
    form_class = PromptForm
    current_contest = None
    sort_by = None
    paginate_by = 20

    def get_queryset(self):
        queryset = Prompt.objects.annotate(num_pictures=Count('pictures')).filter(is_visible=True)

        self.sort_by = self.request.GET.get('sort_by', None)
        if self.sort_by not in ['artist', 'date', 'count']:
            self.sort_by = 'count'

        order_by_map = {
            'artist': ('creator__username',),
            'date': ('-created_at',),
            'count': ('-num_pictures', '-created_at',),
        }
        queryset = queryset.order_by(*order_by_map[self.sort_by])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sort_by'] = self.sort_by

        page_obj = context['page_obj']
        context['pages_link'] = PagesLink(
            len(self.object_list),
            self.paginate_by,
            page_obj.number,
            is_descending=True,
            base_url=self.request.path,
            query_dict=self.request.GET,
        )

        context['form'] = self.get_form()

        return context


class PromptView(UserPaneMixin, DetailView):
    template_name = 'fanart/chamber_of_stars/prompt.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Prompt, pk=self.kwargs['pk'], is_visible=True)


class PromptCreateView(LoginRequiredMixin, CreateView):
    model = Prompt
    form_class = PromptForm

    def form_valid(self, form):
        prompt = form.save(commit=False)
        prompt.creator = self.request.user
        return super().form_valid(form)


class PromptDeactivateView(LoginRequiredMixin, UpdateView):
    model = Prompt
    form_class = PromptDeactivateForm

    def get_object(self, queryset=None):
        return get_object_or_404(Prompt, pk=self.kwargs['pk'], creator=self.request.user)

    def form_valid(self, form):
        prompt = form.save(commit=False)
        prompt.is_visible = False
        prompt.save()
        return JSONResponse({'url': reverse('prompts')})


class PromptEntryCreateView(LoginRequiredMixin, UpdateView):
    model = Prompt
    template_name = 'fanart/chamber_of_stars/prompt.html'
    fields = ()

    def form_valid(self, form):
        prompt = get_object_or_404(Prompt, pk=self.kwargs.get('pk', None))
        picture = get_object_or_404(Picture, pk=self.request.POST.get('picture', None), artist=self.request.user)
        prompt.pictures.add(picture)
        logger.info(f'{self.request.user} posted {picture} to prompt {prompt}')
        return super().form_valid(form)


class PromptEntryDeleteView(LoginRequiredMixin, UpdateView):
    model = Prompt
    fields = ()

    def form_valid(self, form):
        prompt = get_object_or_404(Prompt, pk=self.kwargs.get('pk', None))
        picture = get_object_or_404(Picture, pk=self.request.POST.get('picture', None), artist=self.request.user)
        prompt.pictures.remove(picture)

        logger.info(f'{self.request.user} removed {picture} from prompt {prompt}')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('prompt', kwargs={'prompt_id': self.object.pk})
