from django.conf.urls import url

from . import views
from . import csvExport
from . import ajax

urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^pledgeEntry/$', views.pledgeEntry, name='pledgeEntry'),
    url(r'^report/$', views.report, name='report'),
    url(r'deletePledgeEntry', views.deletePledgeEntry, name='deletePledgeEntry'),
    url(r'^ajax_get_summary', ajax.ajax_get_summary, name='ajax_get_summary'),
    url(r'^ajax_retrieve_latest_entries/$', ajax.ajax_retrieve_latest_entries, name='ajax_retrieve_latest_entries'),
    url(r'^ajax_get_next_entries/$', ajax.ajax_get_next_entries, name='ajax_get_next_entries'),
    url(r'^ajax_thank_id/$', ajax.ajax_thank_id, name='ajax_thank_id'),
    url(r'^editPledgeEntry/$', views.editPledgeEntry, name='editPledgeEntry'),
    url(r'^csvExport/$', csvExport.csvExport, name='csvExport'),
    url(r'^config/$', views.config, name='config'),
    # url(r'^test/$', views.test, name='test'),
]
# 