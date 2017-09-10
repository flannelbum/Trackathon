from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^pledgeEntry/$', views.pledgeEntry, name='pledgeEntry'),
    url(r'deletePledgeEntry', views.deletePledgeEntry, name='deletePledgeEntry'),
    url(r'^ajax_get_summary', views.ajax_get_summary, name='ajax_get_summary'),
    url(r'^ajax_retrieve_latest_entries/$', views.ajax_retrieve_latest_entries, name='ajax_retrieve_latest_entries'),
    url(r'^ajax_get_next_entries/$', views.ajax_get_next_entries, name='ajax_get_next_entries'),
    url(r'^ajax_thank_id/$', views.ajax_thank_id, name='ajax_thank_id'),
    url(r'^editPledgeEntry/$', views.editPledgeEntry, name='editPledgeEntry'),
    url(r'^csvExport/$', views.csvExport, name='csvExport'),
    url(r'^config/$', views.config, name='config'),
    # url(r'^test/$', views.test, name='test'),
]
# 