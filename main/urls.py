from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^pledgeEntry/$', views.pledgeEntry, name='pledgeEntry'),
    url(r'^ajax_get_summary', views.ajax_get_summary, name='ajax_get_summary'),
    url(r'^ajax_retrieve_latest_entries/$', views.ajax_retrieve_latest_entries, name='ajax_retrieve_latest_entries'),
    url(r'^ajax_get_next_entries/$', views.ajax_get_next_entries, name='ajax_get_next_entries'),
]
