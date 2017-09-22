from django.conf.urls import url


from . import ajax
from . import csvExport
from . import views


urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^pledgeEntry/$', views.pledgeEntry, name='pledgeEntry'),
    url(r'^report/$', views.report, name='report'),
    url(r'^entryListDetail/$', views.entryListDetail, name='entryListDetail'),
    url(r'^deletePledgeEntry', views.deletePledgeEntry, name='deletePledgeEntry'),
    url(r'^ajax_retrieve_latest_entries/$', ajax.ajax_retrieve_latest_entries, name='ajax_retrieve_latest_entries'),
    url(r'^ajax_get_next_entries/$', ajax.ajax_get_next_entries, name='ajax_get_next_entries'),
    url(r'^ajax_thank_id/$', ajax.ajax_thank_id, name='ajax_thank_id'),
    url(r'^editPledgeEntry/$', views.editPledgeEntry, name='editPledgeEntry'),
    url(r'^csvExport/$', csvExport.csvExport, name='csvExport'),
]
