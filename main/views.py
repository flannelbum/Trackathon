import csv
import time

from django.conf import settings
<<<<<<< HEAD
=======
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
>>>>>>> refs/heads/travel
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render  # , redirect
from django.template.context_processors import request

from main.customFunctions import getRandomPledgeForm  # , prettydate
from main.forms import PledgeEntryForm
from main.models import PledgeEntry


# from django.core.paginator import Paginator
# Create your views here.
# def test(request):
#   return render(request, 'main/test.html', { 'sumtest': get_summary(3) } )
<<<<<<< HEAD
=======
  

def dashboard(request):
  try:
    latestid = PledgeEntry.objects.latest('id').id
    context = get_summaryData(latestid)
    context['entries'] = PledgeEntry.objects.all().order_by('-id')[:15]
    return render(request, 'main/dashboard.html', context)
  except:
    return render(request, 'main/index.html', {})
  
  
  
>>>>>>> refs/heads/travel
def config(request):
    message = ""
    permitted = False
    context = {}
    cfgpass = request.POST.get('cfgpw', None)
    if cfgpass == settings.CONFIG_PASSWORD:
        permitted = True
        context['cfgpass'] = cfgpass
    else:
        permitted = False
        if request.method == 'GET':
            message += "Please enter the config passowrd"
        else:
            message += "Invalid Password"
    
    context['message'] = message
    context['permitted'] = permitted
    
    return render(request, 'main/config.html', context)
  
  
  
def csvExport(request):
<<<<<<< HEAD
    cfgpw = request.POST.get('cfgpw')
    # print(cfgpw)
=======
  cfgpw = request.POST.get('cfgpw')
  # print(cfgpw)

  if cfgpw == settings.CONFIG_PASSWORD:
    filename = "TrackAThonExport_" + time.strftime("%m%d-%H%M%S") + ".csv"
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + filename
>>>>>>> refs/heads/travel
    
<<<<<<< HEAD
    if cfgpw == settings.CONFIG_PASSWORD:
        filename = "TrackAThonExport_" + time.strftime("%m%d-%H%M%S") + ".csv"
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + filename
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'DATEADDED', 'AMOUNT', 'FIRSTNAME', 'LASTNAME', 'CITY', 'FTD', 'PLEDGETYPE', 'STATION', 'PARISH', 'CALLOUT', 'COMMENT'])
        
        entries = PledgeEntry.objects.all()
        for entry in entries:
            # writer.writerow([ entry.id, entry.create_date.strftime("%Y-%m-%d %H:%m:%S"), entry.amount, entry.firstname, entry.lastname, entry.city, entry.ftdonor, entry.singleormonthly, entry.callsign, entry.parish, entry.groupcallout, entry.comment])
            # # fix up the hour string for -4
            myhour = entry.create_date.strftime("%H")
            myhour = +int(myhour) - 4
            timestr = entry.create_date.strftime("%Y/%m/%d ") + str(myhour) + ":" + entry.create_date.strftime("%M:%S")
            writer.writerow([ entry.id, timestr, entry.amount, entry.firstname, entry.lastname, entry.city, entry.ftdonor, entry.singleormonthly, entry.callsign, entry.parish, entry.groupcallout, entry.comment])
        else:
        # Return silent/404 if blank GET request
            return HttpResponse(status=404)
    return response
=======
    writer = csv.writer(response)
    writer.writerow(['ID','DATEADDED','AMOUNT','FIRSTNAME','LASTNAME','CITY','FTD','PLEDGETYPE','STATION','PARISH','CALLOUT','COMMENT'])
    
    entries = PledgeEntry.objects.all()
    for entry in entries:
      # writer.writerow([ entry.id, entry.create_date.strftime("%Y-%m-%d %H:%m:%S"), entry.amount, entry.firstname, entry.lastname, entry.city, entry.ftdonor, entry.singleormonthly, entry.callsign, entry.parish, entry.groupcallout, entry.comment])
      ## fix up the hour string for -4
      myhour = entry.create_date.strftime("%H")
      myhour =+ int(myhour) - 4
      timestr = entry.create_date.strftime("%Y/%m/%d ") + str(myhour) + ":" + entry.create_date.strftime("%M:%S")
      writer.writerow([ entry.id, timestr, entry.amount, entry.firstname, entry.lastname, entry.city, entry.ftdonor, entry.singleormonthly, entry.callsign, entry.parish, entry.groupcallout, entry.comment])
  else:
    # Return silent/404 if blank GET request
    return HttpResponse(status=404)
  
  return response
  
  
  
def pledgeEntry(request):
  template_name='main/pledgeEntry.html'
  entries = PledgeEntry.objects.order_by('-id')[:20]#[::-1]
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
    print(entry.firstname)
    entry.save()
    form = PledgeEntryForm(None)
    entries = PledgeEntry.objects.order_by('-id')[:20]#[::-1]
    return HttpResponseRedirect('/pledgeEntry/')

  if request.GET.get('getrandom',None):
    # print("getting random pledge")
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

  return render(request, 'main/pledgeEntry.html', { 'form': form,'entries': entries })



def editPledgeEntry(request):
  
  entries = PledgeEntry.objects.order_by('-id')[:20]#[::-1]
  entryid = int_or_0(request.POST.get('entryid'))
  
  if entryid == 0:
    entryid = int_or_0(request.GET.get('entryid'))
  # print(entryid)
  
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
    form.fields["lastname"].initial = p.lastname
    form.fields["city"].initial = p.city
    form.fields["ftdonor"].initial = p.ftdonor
    form.fields["amount"].initial = p.amount
    form.fields["singleormonthly"].initial = p.singleormonthly
    form.fields["callsign"].initial = p.callsign
    form.fields["parish"].initial = p.parish
    form.fields["groupcallout"].initial = p.groupcallout
    form.fields["comment"].initial = p.comment
    
  return render(request, 'main/pledgeEntry.html', { 'form': form, 'entryid': entryid, 'entryObject': p, 'entries': entries })
  

  
def report(request):
  return render(request, 'main/report.html')
  
  
>>>>>>> refs/heads/travel
  
  

def get_summaryData(lid):
    latestid = PledgeEntry.objects.latest('id').id
    entries = PledgeEntry.objects.all()
    
    grand_total = entries.aggregate(Sum('amount'))['amount__sum']
    total_pledges = entries.count()
    total_new_donors = entries.filter(ftdonor__exact=True).count()
    total_new_donor_dollars = entries.filter(ftdonor__exact=True).aggregate(Sum('amount'))['amount__sum']
    total_monthly_donors = entries.filter(singleormonthly__exact="monthly").count()
    total_monthly_dollars = entries.filter(singleormonthly__exact="monthly").aggregate(Sum('amount'))['amount__sum']
    total_single_donors = entries.filter(singleormonthly__exact="single").count()
    total_single_dollars = entries.filter(singleormonthly__exact="single").aggregate(Sum('amount'))['amount__sum']
    
    # ## Possible MySQL snip to prevent the read from locking
    # SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED ;
    # SELECT * FROM TABLE_NAME ;
    # COMMIT ;
    
    sql = "SELECT id, callsign, SUM(amount) AS total, COUNT(id) AS pledges, "
    sql += "SUM(CASE WHEN ftdonor = '1' THEN 1 ELSE 0 END) AS newdonors, "
    sql += "SUM(CASE WHEN singleormonthly = 'monthly' THEN 1 ELSE 0 END) AS monthlies, "
    sql += "SUM(CASE WHEN singleormonthly = 'single' THEN 1 ELSE 0 END) AS singles "
    sql += "FROM main_pledgeentry GROUP BY callsign ORDER BY SUM(amount) DESC "
    
    stations = PledgeEntry.objects.raw(sql)
    
    summaryData = {
        'latestid': latestid,
        'stations': stations,
        'grand_total': grand_total,
        'total_pledges': total_pledges,
        'total_new_donors': total_new_donors,
        'total_new_donor_dollars': total_new_donor_dollars,
        'total_monthly_donors': total_monthly_donors,
        'total_monthly_dollars': total_monthly_dollars,
        'total_single_donors': total_single_donors,
        'total_single_dollars': total_single_dollars,
    }
    # else:
        # print("returning cached summaryData")
      
    return summaryData

  
<<<<<<< HEAD
def dashboard(request):
    try:
        latestid = PledgeEntry.objects.latest('id').id
        context = get_summaryData(latestid)
        context['entries'] = PledgeEntry.objects.all().order_by('-id')[:15]
        return render(request, 'main/dashboard.html', context)
    except:
        return render(request, 'main/index.html', {})
=======

>>>>>>> refs/heads/travel
  
  
  
def ajax_get_summary(request):
    latestid = PledgeEntry.objects.latest('id').id
    context = get_summaryData(latestid)
    return render(request, 'main/summary.html', context)
  
  
  
def int_or_0(value):
    try:
        return int(value)
    except:
        return 0  



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


<<<<<<< HEAD
def deletePledgeEntry(request):
        
    entryid = int_or_0( request.GET.get('entryid') )
    
    p = PledgeEntry.objects.get(pk=entryid)
    p.delete()    

    if 'pledgeEntry' in request.META['HTTP_REFERER']:
        return HttpResponseRedirect('/pledgeEntry/')
    else:
        return HttpResponseRedirect('/')

    
def editPledgeEntry(request):
  
    entries = PledgeEntry.objects.order_by('-id')[:20]  # [::-1]
    entryid = int_or_0(request.POST.get('entryid'))
    
    if entryid == 0:
        entryid = int_or_0(request.GET.get('entryid'))
        # print(entryid)
    
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
        form.fields["lastname"].initial = p.lastname
        form.fields["city"].initial = p.city
        form.fields["ftdonor"].initial = p.ftdonor
        form.fields["amount"].initial = p.amount
        form.fields["singleormonthly"].initial = p.singleormonthly
        form.fields["callsign"].initial = p.callsign
        form.fields["parish"].initial = p.parish
        form.fields["groupcallout"].initial = p.groupcallout
        form.fields["comment"].initial = p.comment
    
    return render(request, 'main/pledgeEntry.html', { 'form': form, 'entryid': entryid, 'entryObject': p, 'entries': entries })
=======
>>>>>>> refs/heads/travel
  


<<<<<<< HEAD
def pledgeEntry(request):
    
#     template_name = 'main/pledgeEntry.html'
    
    entries = PledgeEntry.objects.order_by('-id')[:20]  # [::-1]
    
    form = PledgeEntryForm(request.POST or None)
    
    if form.is_valid():
    
        entry = PledgeEntry(
            firstname=form.cleaned_data['firstname'],
            lastname=form.cleaned_data['lastname'],
            city=form.cleaned_data['city'],
            ftdonor=form.cleaned_data['ftdonor'],
            # beenthanked = form.cleaned_data['beenthanked'],
            amount=form.cleaned_data['amount'],
            singleormonthly=form.cleaned_data['singleormonthly'],
            callsign=form.cleaned_data['callsign'],
            parish=form.cleaned_data['parish'],
            groupcallout=form.cleaned_data['groupcallout'],
            comment=form.cleaned_data['comment'],
            )
        
        print(entry.firstname)
        entry.save()
        form = PledgeEntryForm(None)
        entries = PledgeEntry.objects.order_by('-id')[:20]  # [::-1]
        return HttpResponseRedirect('/pledgeEntry/')
    
    if request.GET.get('getrandom', None):
        # print("getting random pledge")
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
#     
    return render(request, 'main/pledgeEntry.html', { 'form': form, 'entries': entries })
=======
>>>>>>> refs/heads/travel
