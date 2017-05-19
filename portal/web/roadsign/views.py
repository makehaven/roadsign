import django.views.generic
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import ModelFormMixin
from .models import TextPanel, Playlist, PlaylistItem
from .forms import SignPanelFormSet

class Home(LoginRequiredMixin, django.views.generic.TemplateView):
    template_name = "home.html"
home = Home.as_view()


class PlaylistEditor(LoginRequiredMixin, django.views.generic.TemplateView):
    template_name = "editor.html"


class TextPanelCreate(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
         panel = TextPanel()
         panel.save()
         return TextPanelUpdate.as_view()(request, *args, pk=panel.pk, **kwargs)


class TextPanelDelete(LoginRequiredMixin, DeleteView):
    model = TextPanel
    def get_success_url(self):
        return reverse('home')

class TextPanelUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'models/textpanel.html'
    model = TextPanel
    fields = '__all__'


class PlaylistUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'models/playlist.html'
    model = Playlist
    fields = '__all__'
    def get_success_url(self):
        return reverse('playlist_update', kwargs=self.kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        PlaylistItem.objects.filter(playlist_id = self.object.pk).delete()
        for i, panel in enumerate(form.cleaned_data['panels']):
            item = PlaylistItem()
            item.playlist_id = self.object.pk
            item.panel_id = panel.pk
            item.position = i
            item.save()
        self.object.save()
        return super(ModelFormMixin, self).form_valid(form)