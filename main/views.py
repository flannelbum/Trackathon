import datetime
import pytz

from django.conf import settings
from django.http import HttpResponseRedirect
from django.db.models import Sum
from django.shortcuts import render  # , redirect
from collections import OrderedDict

from main.customFunctions import getRandomPledgeForm  # , prettydate
from main.forms import PledgeEntryForm
from main.models import PledgeEntry


# Helper function to return an integer for a given value (string)
#  if none found, return 0
def int_or_0(value):
    try:
        return int(value)
    except:
        return 0 

def dashboard(request):
    try:
        latestid = PledgeEntry.objects.latest('id').id
        context = get_summaryData(latestid)
        context['entries'] = PledgeEntry.objects.all().order_by('-id')[:15]
        return render(request, 'main/dashboard.html', context)
    except:
        return render(request, 'main/index.html', {})
  
  
  
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
    
    
  
def report(request):
    
    context = {}
    daysummary = OrderedDict()
    localtz = pytz.timezone( settings.TIME_ZONE ) # https://stackoverflow.com/questions/24710233/python-convert-time-to-utc-format
    days = PledgeEntry.objects.datetimes('create_date', 'day', 'DESC', localtz) 
    
    for day in days:
        daysummary[day.date().__str__()] = PledgeEntry.objects.filter(create_date__date=datetime.datetime(day.year, day.month, day.day, 0,0, tzinfo=localtz)).count()
    
    context['days'] = daysummary
        
    
    # Get a list of unique days and hours that have pledges
#     startdate = datetime.today()
#     enddate = startdate + timedelta(days=6)
#     Sample.objects.filter(date__range=[startdate, enddate])
# list = PledgeEntry.objects.filter(create_date__range=[])
    
    # returns all entries in the same our has a set entry: e
#     e = PledgeEntry.objects.latest('id')
#     hstart = datetime.datetime( e.create_date.year, e.create_date.month, e.create_date.day, e.create_date.hour, 0, 0, 0, e.create_date.tzinfo )
#     hstop = datetime.datetime(hstart.year, hstart.month, hstart.day, hstart.hour, hstart.minute + 59, hstart.second + 59, hstart.microsecond + 999999, hstart.tzinfo)
#     mylist = PledgeEntry.objects.filter(create_date__range=[hstart, hstop])
#     mylist.count()
    
    
    
    return render(request, 'main/report.html', context)
  
  
  
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

    return render(request, 'main/pledgeEntry.html', { 'form': form, 'entries': entries })
