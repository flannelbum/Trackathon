import time
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from main.forms import PledgeEntryForm
from main.models import PledgeEntry
from main.customFunctions import getRandomPledgeForm, prettydate
# Create your views here.



# def test(request):
#   return render(request, 'main/test.html')


def int_or_0(value):
    try:
        return int(value)
    except:
        return 0
  
  
  
  
def ajax_thank_id(request):
  thankedid = int_or_0(request.POST.get('thankedid',None))
  if thankedid > 0:
    p = PledgeEntry.objects.get(pk=thankedid)
    p.beenthanked = True
    p.save()
  return HttpResponse(status=204)
  
  
  
  
def ajax_get_summary(request):
  entries = PledgeEntry.objects.all()
  grand_total = entries.aggregate(Sum('amount'))['amount__sum']
  total_pledges = entries.count()
  total_new_donors = entries.filter(ftdonor__exact=True).count()
  total_new_donor_dollars = entries.filter(ftdonor__exact=True).aggregate(Sum('amount'))['amount__sum']
  total_new_monthly_dollars = entries.filter(singleormonthly__exact="monthly").aggregate(Sum('amount'))['amount__sum']
  
  # "SELECT id, callsign, SUM(amount) AS total, COUNT(id) AS pledges,  SUM(CASE WHEN ftdonor = '1' THEN 1 ELSE 0 END) AS newdonors, SUM(CASE WHEN singleormonthly = 'monthly' THEN 1 ELSE 0 END) AS monthlies FROM main_pledgeentry GROUP BY callsign ORDER BY SUM(amount) DESC"
    
  sql = "SELECT id, callsign, SUM(amount) AS total, COUNT(id) AS pledges, "
  sql += "SUM(CASE WHEN ftdonor = '1' THEN 1 ELSE 0 END) AS newdonors, "
  sql += "SUM(CASE WHEN singleormonthly = 'monthly' THEN 1 ELSE 0 END) AS monthlies, "
  sql += "SUM(CASE WHEN singleormonthly = 'single' THEN 1 ELSE 0 END) AS singles "
  sql += "FROM main_pledgeentry GROUP BY callsign ORDER BY SUM(amount) DESC"

  stations = PledgeEntry.objects.raw(sql)
  
  context = {
      'stations': stations,
      'grand_total': grand_total,
      'total_pledges': total_pledges,
      'total_new_donors': total_new_donors,
      'total_new_donor_dollars': total_new_donor_dollars,
      'total_new_monthly_dollars': total_new_monthly_dollars,
      }

  return render(request, 'main/summary.html', context)
  
  


def ajax_get_next_entries(request):
  lid = int_or_0(request.GET.get('lid', None))
  entries = PledgeEntry.objects.filter(id__lt=lid).order_by('-id')[:15]
  return render(request, 'main/multiple_pledges.html', { 'entries': entries })
  
  
  
  
def ajax_retrieve_latest_entries(request):

    lid = int_or_0(request.GET.get('lid', None))
    latestid = PledgeEntry.objects.latest('id').id
    maxbehind = 15 # Don't fetch more than this
    behind = latestid - lid
    
    
    if lid == latestid:
      return HttpResponse(status=204)
    
    if lid > latestid:
      return HttpResponse("?lid= greater than actual latest id",status=400)
    
    if lid < 1:
      return HttpResponse("?lid= out of bounds",status=400)
    
    if behind > maxbehind:
      return HttpResponse("?lid= too much to return",status=400)
      
    if latestid > lid:
      entries = PledgeEntry.objects.order_by('-id')[:behind:1]
      return render(request, 'main/multiple_pledges.html', { 'entries': entries })
      



def dashboard(request):
    freshvisit = True
    
    entries = PledgeEntry.objects.all().order_by('-id')
    
    grand_total = entries.aggregate(Sum('amount'))['amount__sum']
    total_pledges = entries.count()
    total_new_donors = entries.filter(ftdonor__exact=True).count()
    total_new_donor_dollars = entries.filter(ftdonor__exact=True).aggregate(Sum('amount'))['amount__sum']
    total_new_monthly_dollars = entries.filter(singleormonthly__exact="monthly").aggregate(Sum('amount'))['amount__sum']
    latestid = PledgeEntry.objects.latest('id').id
    
    sql = "SELECT id, callsign, SUM(amount) AS total, COUNT(id) AS pledges, "
    sql += "SUM(CASE WHEN ftdonor = '1' THEN 1 ELSE 0 END) AS newdonors, "
    sql += "SUM(CASE WHEN singleormonthly = 'monthly' THEN 1 ELSE 0 END) AS monthlies, "
    sql += "SUM(CASE WHEN singleormonthly = 'single' THEN 1 ELSE 0 END) AS singles "
    sql += "FROM main_pledgeentry GROUP BY callsign ORDER BY SUM(amount) DESC"
    
    stations = PledgeEntry.objects.raw(sql)

    context = {
        'entries': entries[:15],
        'stations': stations,
        'grand_total': grand_total,
        'total_pledges': total_pledges,
        'total_new_donors': total_new_donors,
        'total_new_donor_dollars': total_new_donor_dollars,
        'total_new_monthly_dollars': total_new_monthly_dollars,
        'freshvisit': freshvisit,
        'latestid': latestid,
        }

    return render(request, 'main/dashboard.html', context)




def editPledgeEntry(request):
  entryid = int_or_0(request.POST.get('entryid'))
  if entryid == 0:
    entryid = int_or_0(request.GET.get('entryid'))
  print(entryid)
  p = PledgeEntry.objects.get(pk=entryid)
  if request.method == "POST":
    form = PledgeEntryForm(request.POST or None)
    if form.is_valid():
      p.firstname = form.cleaned_data['firstname']
      p.lastname = form.cleaned_data['lastname']
      p.city = form.cleaned_data['city']
      p.ftdonor = form.cleaned_data['ftdonor']
      p.amount = form.cleaned_data['amount']
      p.singleormonthly = form.cleaned_data['singleormonthly']
      p.callsign = form.cleaned_data['callsign']
      p.parish = form.cleaned_data['parish']
      p.groupcallout = form.cleaned_data['groupcallout']
      p.comment = form.cleaned_data['comment']
      p.save()
      form = PledgeEntryForm(None)
      return HttpResponseRedirect('/pledgeEntry/')
      
  else:
    form = PledgeEntryForm(None)
    form.fields["firstname"].initial = p.firstname
    # form.firstname = p.firstname
    form.fields["lastname"].initial = p.lastname
    form.fields["city"].initial = p.city
    form.fields["ftdonor"].initial = p.ftdonor
    form.fields["amount"].initial = p.amount
    form.fields["singleormonthly"].initial = p.singleormonthly
    form.fields["callsign"].initial = p.callsign
    form.fields["parish"].initial = p.parish
    form.fields["groupcallout"].initial = p.groupcallout
    form.fields["comment"].initial = p.comment
  return render(request, 'main/pledgeEntry.html', { 'form': form, 'entryid': entryid, 'entryObject': p })
  



def pledgeEntry(request):
    template_name='main/pledgeEntry.html'
    entries = PledgeEntry.objects.order_by('-id')[:10][::-1]
    # entries = PledgeEntry.objects.order_by('-id')[:10:1]

    form = PledgeEntryForm(request.POST or None)

    if form.is_valid():

        entry = PledgeEntry(
            firstname = form.cleaned_data['firstname'],
            lastname = form.cleaned_data['lastname'],
            city = form.cleaned_data['city'],
            ftdonor = form.cleaned_data['ftdonor'],
            # beenthanked = form.cleaned_data['beenthanked'],
            amount = form.cleaned_data['amount'],
            singleormonthly = form.cleaned_data['singleormonthly'],
            callsign = form.cleaned_data['callsign'],
            parish = form.cleaned_data['parish'],
            groupcallout = form.cleaned_data['groupcallout'],
            comment = form.cleaned_data['comment'],
        )
        entry.save()
        form = PledgeEntryForm(None)
        entries = PledgeEntry.objects.order_by('-id')[:10][::-1]


    if request.GET.get('getrandom',None):
        print("getting random pledge")
        myform = getRandomPledgeForm()
        form.fields["firstname"].initial = myform.firstname
        form.fields["lastname"].initial = myform.lastname
        form.fields["city"].initial = myform.city
        form.fields["ftdonor"].initial = myform.ftdonor
        # form.fields["beenthanked"].initial = myform.beenthanked
        form.fields["amount"].initial = myform.amount
        form.fields["singleormonthly"].initial = myform.singleormonthly
        form.fields["callsign"].initial = myform.callsign
        form.fields["parish"].initial = myform.parish
        form.fields["groupcallout"].initial = myform.groupcallout
        form.fields["comment"].initial = myform.comment


    return render(
        request,
        template_name, {
            'form': form,
            'entries': reversed(entries),
        },
    )
