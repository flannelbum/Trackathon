from django.http.response import HttpResponse
from django.shortcuts import render

from main.models import PledgeEntry
from main.views import int_or_0


def ajax_get_next_entries(request):
    lid = int_or_0(request.GET.get('lid', None))
    entries = PledgeEntry.objects.filter(id__lt=lid).order_by('-id')[:15]
    return render(request, 'main/multiple_pledges.html', { 'entries': entries })
  
 
 
def ajax_thank_id(request):
    thankedid = int_or_0(request.POST.get('thankedid', None))
    if thankedid > 0:
        p = PledgeEntry.objects.get(pk=thankedid)
        p.beenthanked = True
        p.save()
    return HttpResponse(status=204)
 

  
def ajax_retrieve_latest_entries(request):

    lid = int_or_0(request.GET.get('lid', None))
    latestid = PledgeEntry.objects.latest('id').id
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
        entries = PledgeEntry.objects.order_by('-id')[:behind:1]
        return render(request, 'main/multiple_pledges.html', { 'entries': entries })
    
    # # Should not make it this far but, just in case, stay quiet
    return HttpResponse(status=204)
