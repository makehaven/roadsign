from django.db import models
from enumfields import EnumField, Enum
from polymorphic.models import PolymorphicModel

class SignStatusType(Enum):
    CHECKING = "Checking"
    OFFLINE = "Offline"
    ACTIVE = "Active"
    UPDATING = "Updating"
    FAILED = "Failed"


class Sign(models.Model):
    name = models.CharField(max_length=255)
    particle_id = models.CharField(max_length=255)
    status = EnumField(SignStatusType)
    code_hash = models.CharField(max_length=255, blank=True)


class SignPanel(PolymorphicModel):
    pass


class ImagePanel(SignPanel):
    image = models.ImageField()


class TextPanel(SignPanel):
    num_lines = models.IntegerField(default=3)
    line1 = models.CharField(max_length=255, blank=True)
    line2 = models.CharField(max_length=255, blank=True)
    line3 = models.CharField(max_length=255, blank=True)


class Playlist(models.Model):
    name = models.CharField(max_length = 255)
    panels = models.ManyToManyField('SignPanel', through='PlaylistItem', blank=True)

class PlaylistItem(models.Model):
    playlist = models.ForeignKey('Playlist')
    panel =    models.ForeignKey('SignPanel')
    position = models.IntegerField()

    class Meta:
        ordering = ['position']
