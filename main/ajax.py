from django.http.response import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from main.models import Pledge
from main.customFunctions import int_or_0
from main.views import decode_entries
from main.GoalTender import update_goals



def ajax_get_next_listDetail(request):
    lid = int_or_0(request.GET.get('lid', None))
    entries = decode_entries(request.GET.get('list'))
    if lid == 0:
        return HttpResponse(status=204)
    if entries.count() < 1:
        return HttpResponse(status=204)
    if lid == entries.latest('id').id:
        return HttpResponse(status=204)
    
    return render(request, 'main/multiple_pledges.html', { 'entries': entries.filter(id__gt=lid)[:15] })



def ajax_get_next_entries(request):
    lid = int_or_0(request.GET.get('lid', None))
    entries = Pledge.objects.campaign_active().filter(id__lt=lid).order_by('-id')[:15]
    return render(request, 'main/multiple_pledges.html', { 'entries': entries })
  
 
#TODO: update applicable goal(s) raised amount(s) by thanked pledge object amount
def ajax_thank_id(request):
    thankedid = int_or_0(request.POST.get('thankedid', None))
    if thankedid > 0:
        p = Pledge.objects.get(pk=thankedid)
        p.is_thanked = True
        p.thanked_datetime = timezone.now()
        p.save()
        update_goals(p, p.amount)
    return HttpResponse(status=204)
 

  
def ajax_retrieve_latest_entries(request):

    lid = int_or_0(request.GET.get('lid', None))
    latestid = Pledge.objects.campaign_active().latest('id').id
    maxbehind = 15  # Don't fetch more than this
    behind = latestid - lid
    
    if lid == latestid:
        return HttpResponse(status=204)
    
    if lid > latestid:
        return HttpResponse("?lid= greater than actual latest id of " + str(latestid), status=400)
    
    if lid < 1:
        return HttpResponse("?lid= must be greater than 0", status=400)
    
    if behind > maxbehind:
        return HttpResponse("Too much to return.  ?lid= must currently be between " + str(latestid - maxbehind) + " - " + str(latestid), status=400)
      
    if latestid > lid:
        entries = Pledge.objects.campaign_active().order_by('-id')[:behind:1]
        return render(request, 'main/multiple_pledges.html', { 'entries': entries })
    
    # # Should not make it this far but, just in case, stay quiet
    return HttpResponse(status=204)
