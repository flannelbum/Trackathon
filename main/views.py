from base64 import urlsafe_b64encode, urlsafe_b64decode
import calendar
from collections import OrderedDict
import datetime
import itertools

from django.conf import settings
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render
import pytz
from tagging.models import Tag, TaggedItem

from main.customFunctions import getRandomPledgeForm, int_or_0
from main.forms import PledgeEntryForm
from main.models import Pledge, Station


def dashboard(request):
    try:
        context = {}
        context['overall_totals_summaryData'] = get_summaryData( "Campaign Overall", Pledge.objects.all(), None )
        
        # get latest entry
        latestentry = Pledge.objects.all().latest('create_date')
        context['lid'] = latestentry.id
        
        # get all entries in the same day as latest
        day_entries = Pledge.objects.filter(create_date__date=( latestentry.create_date ))
        context['latest_day_summaryData'] = get_summaryData( "Current Day", day_entries, None)
        
        # all entires for the latest hour
        latest_entries = get_entries_in_same_hour_as(latestentry)
        context['latest_hour_summaryData'] = get_summaryData( "Current Hour", latest_entries, None) 
        
        # all entires for the previous hour
        
        if latestentry.create_date.hour > 0:
            olderthan = datetime.datetime.combine( latestentry.create_date.date(), datetime.time( latestentry.create_date.hour -1, 59, 59, 999999, tzinfo=pytz.UTC))
        else:
            olderthan = datetime.datetime.combine( latestentry.create_date.date(), datetime.time( 23, 59, 59, 999999, tzinfo=pytz.UTC))
            
        # prevent exception when we're in our first hour
        try:
            previous_entry = Pledge.objects.filter(create_date__lte=olderthan).latest('create_date')
            previous_entries = get_entries_in_same_hour_as(previous_entry)
            context['previous_hour_summaryData'] = get_summaryData( "Previous Hour", previous_entries, None)
        except Pledge.DoesNotExist:
            pass
        
        # initial entries context for the acccordian list
        context['entries'] = Pledge.objects.all().order_by('-id')[:15]
        return render(request, 'main/dashboard.html', context)
    
    except:
        return render(request, 'main/index.html', {})
    
    

def get_entries_in_same_hour_as(entry):
    starttime = datetime.datetime.combine( entry.create_date.date(), datetime.time( entry.create_date.hour, 0, 0, 0, tzinfo=pytz.UTC))
    endtime = datetime.datetime.combine( starttime.date(), datetime.time( starttime.hour, 59, 59, 999999, tzinfo=pytz.UTC))
    return Pledge.objects.filter(create_date__range=( starttime, endtime ))
    
    
  
def report(request):
    
    context = {}
    daySummary = OrderedDict()
    localtz = pytz.timezone( settings.TIME_ZONE ) # https://stackoverflow.com/questions/24710233/python-convert-time-to-utc-format
    days = Pledge.objects.datetimes('create_date', 'day', 'DESC', localtz) 
       
    dayDetail = request.GET.get('dayDetail', None)
    
    for day in days:       
        label = calendar.day_name[day.weekday()] + ", " + str(day.month) + "/" + str(day.day) + "/" + str(day.year)
        entries = Pledge.objects.filter(create_date__date=datetime.datetime(day.year, day.month, day.day, 0,0, tzinfo=localtz))
        count = entries.count()
        
        if dayDetail == day.date().__str__():
            context['date'] = datetime.date(day.year, day.month, day.day)
            context['hourlyBreakdown'] = hourlyBreakdown(entries)
                        
        daySummary[day.date().__str__()] = {'dayDetail': day.date().__str__(), 'label': label, 'count': count, 'summaryData': get_summaryData(label, entries, None)}
        context['daySummary'] = daySummary
        
    return render(request, 'main/report.html', context)
   
    
    
def date_hour(_datetime):
    _dt = _datetime.astimezone( pytz.timezone( settings.TIME_ZONE))
    return _dt.strftime("%I:00 %p") #ex: 05:00 PM

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
        qs = Pledge.objects.filter(id__in=hrlyids)
        
        createdate = entry.create_date
        timestring = createdate.astimezone( pytz.timezone( settings.TIME_ZONE ))
        
        label = group + " Breakdown for " + timestring.strftime("%b %d, %Y") 

        hbd[group] = {'count': len(hrlyids), 'summaryData': get_summaryData(label, qs, None), 'entries': qs}
         
    return hbd
    
  
def encode_entryIDs(entries):
    try:
        entryids = [str(entry.id) for entry in entries]
        entryidstring = ",".join(entryids) 
        
        encodedentryidstring = urlsafe_b64encode(entryidstring.encode())
        return encodedentryidstring
    except:
        return None
  
def decode_entryIDs(encodedstring):
    decodedentryidstring = urlsafe_b64decode(encodedstring.encode('ascii'))
    
    idlist = decodedentryidstring.split(b',')
    entries = Pledge.objects.filter(id__in=idlist)
    return entries
      
  
def get_taglist(entries, topnum):
    taglist = OrderedDict()
    
    tags = Tag.objects.usage_for_queryset(entries, counts=True, min_count=None)
    tags.sort(key=lambda x: x.count, reverse=True)
    for tag in tags:
        tagged = TaggedItem.objects.get_by_model(entries, tag)
        taglist[tag.count.__str__() + "-" + tag.name] = tag.name, tagged.aggregate(Sum('amount'))['amount__sum'], encode_entryIDs(tagged)
            
    if topnum != None:
        int(topnum)
        while len(taglist) > topnum:
            taglist.popitem()
            
    return taglist


def get_summaryData(label, entries, stations):
    latestid = Pledge.objects.latest('id').id
    
    if entries == None:
        entries = Pledge.objects.all()

    total_entries = encode_entryIDs(entries)
    total_dollars = entries.aggregate(Sum('amount'))['amount__sum']
    total_pledges = entries.count()
    
    nd_entries = entries.filter(is_first_time_donor__exact=True)
    new_entries = encode_entryIDs(nd_entries)
    new_donors = nd_entries.count()
    new_donor_dollars = nd_entries.aggregate(Sum('amount'))['amount__sum']
    
    md_entries = entries.filter(is_monthly__exact=True)
    monthly_entries = encode_entryIDs(md_entries)
    monthly_donors = md_entries.count()
    monthly_dollars = md_entries.aggregate(Sum('amount'))['amount__sum']
    
    sd_entries = entries.filter(is_monthly__exact=False)
    single_entries = encode_entryIDs(sd_entries)
    single_donors = sd_entries.count()
    single_dollars = sd_entries.aggregate(Sum('amount'))['amount__sum']
    
    # if we were told station data, we need full tags too
    stationData = {}
    if stations:
        for station in stations:
            station_entries = entries.filter(station=station)
            if station_entries.count() > 0:
                stationData[station.callsign] = get_summaryData(None, station_entries, None)        
        tags = get_taglist(entries, None)
    else:
        tags = get_taglist(entries, 7)
    
    summaryData = {
        'label': label,
        'latestid': latestid, # don't think this should be here
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
        'tags': tags,
    }
      
    if len(stationData) > 0:
        summaryData['stationData'] = stationData
        
    return summaryData

  
def entryListDetail(request):
    entries = decode_entryIDs(request.GET.get('list'))
    label = request.GET.get('label')
    summaryData = get_summaryData(label, entries, Station.objects.all() )
    return render(request, 'main/entryListDetail.html', { 'label': label, 'summaryData': summaryData, 'entries': entries })
  

def deletePledgeEntry(request):
        
    entryid = int_or_0( request.GET.get('entryid') )
    
    p = Pledge.objects.get(pk=entryid)
    p.delete()    

    if 'pledgeEntry' in request.META['HTTP_REFERER']:
        return HttpResponseRedirect('/pledgeEntry/')
    elif 'report' in request.META['HTTP_REFERER']:
        return HttpResponseRedirect('/report/') 
    elif 'entryListDetail' in request.META['HTTP_REFERER']:
        return HttpResponseRedirect('/report/')
    else:
        return HttpResponseRedirect('/')

    
    
def editPledgeEntry(request):
  
    entries = Pledge.objects.order_by('-id')[:20]  # [::-1]
    entryid = int_or_0(request.POST.get('entryid'))
    
    if entryid == 0:
        entryid = int_or_0(request.GET.get('entryid'))
    
    p = Pledge.objects.get(pk=entryid)
    
    if request.method == "POST":
        form = PledgeEntryForm(request.POST or None)
        if form.is_valid():
                        
            p.firstname = form.cleaned_data['firstname']
            p.lastname = form.cleaned_data['lastname']
            p.city = form.cleaned_data['city']
            p.amount = form.cleaned_data['amount']
            p.is_first_time_donor = form.cleaned_data['is_first_time_donor']
            p.is_monthly = form.cleaned_data['is_monthly']
            p.station = form.cleaned_data['station']
            p.tags = form.cleaned_data['tags']
            p.comment = form.cleaned_data['comment']
            p.save()
            form = PledgeEntryForm(None)
            return HttpResponseRedirect('/pledgeEntry/')
      
    else:
        
        taglist = list(p.tags.values_list('name', flat=True))
        tags = ", ".join(taglist) 
        
        form = PledgeEntryForm(None)
        form.fields["firstname"].initial = p.firstname
        form.fields["lastname"].initial = p.lastname
        form.fields["city"].initial = p.city
        form.fields["amount"].initial = p.amount
        form.fields["is_monthly"].initial = p.is_monthly
        form.fields["is_first_time_donor"].initial = p.is_first_time_donor
        form.fields["station"].initial = p.station
        form.fields["tags"].initial = tags
        form.fields["comment"].initial = p.comment
    
    return render(request, 'main/pledgeEntry.html', { 'form': form, 'entryid': entryid, 'entryObject': p, 'entries': entries })


def pledgeEntry(request):
    
    entries = Pledge.objects.order_by('-id')[:20]  # [::-1]
    
    form = PledgeEntryForm(request.POST or None)
    
    if form.is_valid():
    
        entry = Pledge(
            firstname=form.cleaned_data['firstname'],
            lastname=form.cleaned_data['lastname'],
            city=form.cleaned_data['city'],
            amount=form.cleaned_data['amount'],
            is_first_time_donor=form.cleaned_data['is_first_time_donor'],
            is_monthly=form.cleaned_data['is_monthly'],
            station=form.cleaned_data['station'],
            comment=form.cleaned_data['comment'],
            )

        # tags are special.  Have to have an entry before we can tag it.
        entry.save()
        entry.tags = form.cleaned_data['tags']
        entry.save()
        
        form = PledgeEntryForm(None)
        entries = Pledge.objects.order_by('-id')[:20]  # [::-1]
        return HttpResponseRedirect('/pledgeEntry/')
    
    if request.GET.get('getrandom', None):
        myform = getRandomPledgeForm()
        form.fields["firstname"].initial = myform.firstname
        form.fields["lastname"].initial = myform.lastname
        form.fields["city"].initial = myform.city
        form.fields["amount"].initial = myform.amount
        form.fields["is_first_time_donor"].initial = myform.is_first_time_donor
        form.fields["is_monthly"].initial = myform.is_monthly
        form.fields["station"].initial = myform.station
        form.fields["tags"].initial = myform.tags
        form.fields["comment"].initial = myform.comment

    return render(request, 'main/pledgeEntry.html', { 'form': form, 'entries': entries })
