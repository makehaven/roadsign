from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from . import models

admin.site.register(models.Sign)
admin.site.register(models.Playlist)
admin.site.register(models.PlaylistItem)

class SignPanelChildAdmin(PolymorphicChildModelAdmin):
    """ Base admin class for all child models """
    base_model = models.SignPanel


@admin.register(models.TextPanel)
class TextPanelAdmin(SignPanelChildAdmin):
    base_model = models.SignPanel


@admin.register(models.ImagePanel)
class ImagePanelAdmin(SignPanelChildAdmin):
    base_model = models.ImagePanel
    # define custom features here


@admin.register(models.SignPanel)
class SignPanelParentAdmin(PolymorphicParentModelAdmin):
    """ The parent model admin """
    base_model = models.SignPanel
    child_models = (models.TextPanel, models.ImagePanel)