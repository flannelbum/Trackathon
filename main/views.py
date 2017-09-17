from base64 import urlsafe_b64encode, urlsafe_b64decode
import calendar
from collections import OrderedDict
import datetime
import itertools

from django.conf import settings
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from django.shortcuts import render  # , redirect
import pytz

from main.customFunctions import getRandomPledgeForm, int_or_0  # , prettydate
from main.forms import PledgeEntryForm
from main.models import PledgeEntry


def dashboard(request):
# try:
    context = {}
    context['overall_totals_summaryData'] = get_summaryData( PledgeEntry.objects.all(), "Overall Totals" )
    
    # get latest entry
    latestentry = PledgeEntry.objects.all().latest('create_date')
    
    # get all entries in the same day as latest
    day_entries = PledgeEntry.objects.filter(create_date__date=( latestentry.create_date ))
    context['latest_day_summaryData'] = get_summaryData(day_entries, "Latest Day Totals")
    
    # all entires for the latest hour
    latest_entries = get_entries_in_same_hour_as(latestentry)
    context['latest_hour_summaryData'] = get_summaryData(latest_entries, "Latest Hour Totals") 
    
    # all entires for the previous hour
    olderthan = datetime.datetime.combine( latestentry.create_date.date(), datetime.time( latestentry.create_date.hour -1, 59, 59, 999999, tzinfo=pytz.UTC))

    previous_entry = PledgeEntry.objects.filter(create_date__lte=olderthan).latest('create_date')
    previous_entries = get_entries_in_same_hour_as(previous_entry)
    context['previous_hour_summaryData'] = get_summaryData(previous_entries, "Previous Hour Totals")
    
    # initial entries context for the acccordian list
    context['entries'] = PledgeEntry.objects.all().order_by('-id')[:15]
    return render(request, 'main/dashboard.html', context)

# except:
#     return render(request, 'main/index.html', {})
    
    

def get_entries_in_same_hour_as(entry):
    starttime = datetime.datetime.combine( entry.create_date.date(), datetime.time( entry.create_date.hour, 0, 0, 0, tzinfo=pytz.UTC))
    endtime = datetime.datetime.combine( starttime.date(), datetime.time( starttime.hour, 59, 59, 999999, tzinfo=pytz.UTC))
    return PledgeEntry.objects.filter(create_date__range=( starttime, endtime ))
  
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
            message += "Please enter the config password"
        else:
            message += "Invalid Password"
    
    context['message'] = message
    context['permitted'] = permitted
    
    return render(request, 'main/config.html', context)
    
    
  
def report(request):
    
    context = {}
    daySummary = OrderedDict()
    localtz = pytz.timezone( settings.TIME_ZONE ) # https://stackoverflow.com/questions/24710233/python-convert-time-to-utc-format
    days = PledgeEntry.objects.datetimes('create_date', 'day', 'DESC', localtz) 
       
    dayDetail = request.GET.get('dayDetail', None)
    
    for day in days:       
        label = calendar.day_name[day.weekday()] + ", " + str(day.month) + "/" + str(day.day) + "/" + str(day.year)
        entries = PledgeEntry.objects.filter(create_date__date=datetime.datetime(day.year, day.month, day.day, 0,0, tzinfo=localtz))
        count = entries.count()
        
        if dayDetail == day.date().__str__():
            context['date'] = datetime.date(day.year, day.month, day.day)
            context['hourlyBreakdown'] = hourlyBreakdown(entries)
                        
        daySummary[day.date().__str__()] = {'dayDetail': day.date().__str__(), 'label': label, 'count': count, 'summaryData': get_summaryData(entries, label)}
        context['daySummary'] = daySummary
        
    return render(request, 'main/report.html', context)
   
    
    
def date_hour(_datetime):
    #09/14/17 05 PM
    #return _datetime.strftime("%x %I %p")
    #05:00 PM
    _dt = _datetime.astimezone( pytz.timezone( settings.TIME_ZONE))
    return _dt.strftime("%I:00 %p")    

def hourlyBreakdown(entries):
    hbd = OrderedDict()
    
    groups = itertools.groupby(entries, lambda x:date_hour( x.create_date)) 
    #since groups is an iterator and not a list you have not yet traversed the list
    for group,matches in groups: #now you are traversing the list ...
#         print group,"TTL:",sum(1 for _ in matches)
        hrlyids = []
        count = 0
        for entry in matches:
            count = count + 1
            hrlyids.append(entry.id)
        qs = PledgeEntry.objects.filter(id__in=hrlyids)
        
        createdate = entry.create_date
        timestring = createdate.astimezone( pytz.timezone( settings.TIME_ZONE ))
        
        label = group + " Breakdown for " + timestring.strftime("%b %d, %Y") 

        hbd[group] = {'count': len(hrlyids), 'summaryData': get_summaryData(qs, label), 'entries': qs}
         
    return hbd
    
  
def encode_entryIDs(entries):
    try:
        entryids = [str(entry.id) for entry in entries]
        entryidstring = ",".join(entryids) 
        encodedentryidstring = urlsafe_b64encode(entryidstring)
        return encodedentryidstring
    except:
        return None
  
def decode_entryIDs(encodedstring):
    decodedentryidstring = urlsafe_b64decode(encodedstring.encode('ascii'))
    
    idlist = decodedentryidstring.split(',')
    testentries = PledgeEntry.objects.filter(id__in=idlist)
    return testentries
      
  
def get_summaryData(entries, label):
    latestid = PledgeEntry.objects.latest('id').id
    
    if entries == None:
        entries = PledgeEntry.objects.all()
    
    total_entries = encode_entryIDs(entries)
    total_dollars = entries.aggregate(Sum('amount'))['amount__sum']
    total_pledges = entries.count()
    
    nd_entries = entries.filter(ftdonor__exact=True)
    new_entries = encode_entryIDs(nd_entries)
    new_donors = nd_entries.count()
    new_donor_dollars = nd_entries.aggregate(Sum('amount'))['amount__sum']
    
    md_entries = entries.filter(singleormonthly__exact="monthly")
    monthly_entries = encode_entryIDs(md_entries)
    monthly_donors = md_entries.count()
    monthly_dollars = md_entries.aggregate(Sum('amount'))['amount__sum']
    
    sd_entries = entries.filter(singleormonthly__exact="single")
    single_entries = encode_entryIDs(sd_entries)
    single_donors = sd_entries.count()
    single_dollars = sd_entries.aggregate(Sum('amount'))['amount__sum']
    
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
        'label': label,
        'latestid': latestid,
        'stations': stations,
        'total_entries': total_entries,
        'total_dollars': total_dollars,
        'total_pledges': total_pledges,
        'new_entries': new_entries,
        'new_donors': new_donors,
        'new_donor_dollars': new_donor_dollars,
        'monthly_entries': monthly_entries,
        'monthly_donors': monthly_donors,
        'monthly_dollars': monthly_dollars,
        'single_entries': single_entries,
        'single_donors': single_donors,
        'single_dollars': single_dollars,
    }
      
    return summaryData

  
def entryListDetail(request):
    entries = decode_entryIDs(request.GET.get('list'))
    label = request.GET.get('label')
    return render(request, 'main/entryListDetail.html', { 'label': label, 'entries': entries })
  

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
