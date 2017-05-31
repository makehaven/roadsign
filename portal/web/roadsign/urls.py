from django.conf.urls import url

from . import views

urlpatterns = [
    # A view named "home" is referenced in a few places.
    # Make sure to update the references if you change or delete this url line!
    url(r"^$", views.home, name="home"),
    url(r'textpanel/create/$', views.TextPanelCreate.as_view(), name='textpanel_create'),
    url(r'textpanel/update/(?P<pk>\d+)/$', views.TextPanelUpdate.as_view(), name='textpanel_update'),
    url(r'textpanel/delete/(?P<pk>\d+)/$', views.TextPanelDelete.as_view(), name='textpanel_delete'),
    url(r'playlist/create/$', views.PlaylistCreate.as_view(), name='playlist_create'),
    url(r'playlist/update/(?P<pk>\d+)/$', views.PlaylistUpdate.as_view(), name='playlist_update'),
    url(r'panel/update/(?P<pk>\d+)/$', views.PanelUpdate.as_view(), name='panel_update'),
    url(r'editor/(?P<pk>\d+)/$', views.PlaylistEditor.as_view(), name='editor'),
    url(r'playlist/list/$', views.PlaylistList.as_view(), name='playlist_list'),
    url(r'playlist/delete/(?P<pk>\d+)/$', views.PlaylistDelete.as_view(), name='playlist_delete'),
]
