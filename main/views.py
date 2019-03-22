from base64 import urlsafe_b64encode, urlsafe_b64decode
import calendar
from collections import OrderedDict
import datetime
from datetime import timedelta
import itertools

from django.conf import settings
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
import pytz
from tagging.models import Tag, TaggedItem

from main.customFunctions import getRandomPledgeForm, int_or_0
from main.forms import PledgeEntryForm
from main.models import Pledge, Station, Campaign
from tagging.utils import parse_tag_input
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required


def login_view(request):
    
    if request.POST.get('next'):
        nextpage = request.POST.get('next')
    else:
        nextpage = 'dashboard'
    
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(nextpage)
    else:
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})


def dashboard(request):
    try:
        context = {}
        context['overall_totals_summaryData'] = get_summaryData( "Campaign Overall", Pledge.objects.campaign_active().all(), None )
        
        # get latest entry
        latestentry = Pledge.objects.campaign_active().all().latest('create_date')
        context['lid'] = latestentry.id
        
        # get all entries in the same day as latest
        day_entries = Pledge.objects.campaign_active().filter(create_date__date=( latestentry.create_date ))
        context['latest_day_summaryData'] = get_summaryData( "Current Day", day_entries, None)
        
        # all entries for the latest hour
        latest_entries = get_entries_in_same_hour_as(latestentry)
        context['latest_hour_summaryData'] = get_summaryData( "Current Hour", latest_entries, None) 
        
        # all entries for the previous hour
        
        if latestentry.create_date.hour > 0:
            olderthan = datetime.datetime.combine( latestentry.create_date.date(), datetime.time( latestentry.create_date.hour -1, 59, 59, 999999, tzinfo=pytz.UTC))
        else:
            olderthan = datetime.datetime.combine( latestentry.create_date.date(), datetime.time( 23, 59, 59, 999999, tzinfo=pytz.UTC))
            
        # prevent exception when we're in our first hour
        try:
            previous_entry = Pledge.objects.campaign_active().filter(create_date__lte=olderthan).latest('create_date')
            previous_entries = get_entries_in_same_hour_as(previous_entry)
            context['previous_hour_summaryData'] = get_summaryData( "Previous Hour", previous_entries, None)
        except Pledge.DoesNotExist:
            pass
        
        # initial entries context for the accordion list
        context['entries'] = Pledge.objects.campaign_active().all().order_by('-id')[:15]
        return render(request, 'main/dashboard.html', context)
    
    except:
        return render(request, 'main/index.html', {})
    
    
def get_entries_in_same_hour_as(entry):
    starttime = datetime.datetime.combine( entry.create_date.date(), datetime.time( entry.create_date.hour, 0, 0, 0, tzinfo=pytz.UTC))
    endtime = datetime.datetime.combine( starttime.date(), datetime.time( starttime.hour, 59, 59, 999999, tzinfo=pytz.UTC))
    return Pledge.objects.campaign_active().filter(create_date__range=( starttime, endtime ))
    
  
def get_campaigns():
    campaigns = {}
    for campaign in Campaign.objects.all():
        campaigns[campaign.id] = campaign.name + ' (' + str(Pledge.objects.campaign_past_id(campaign.id).count()) + ')' 
    return campaigns  
  
  
import sys
import django
@login_required(login_url='/login/')
def TATsettings(request):

    context = {}

    if request.POST.get('logout'):
        logout(request)
        return redirect('dashboard')
    
    if request.POST.get('new_campaign_name'):
        new_campaign = request.POST.get('new_campaign_name')    
        campaign = Campaign.objects.create(name=new_campaign)
        for pledge in Pledge.objects.campaign_active():
            pledge.campaign = campaign
            pledge.save()
        return redirect('/report/?campaignid=' + str(campaign.id))
    
    if request.POST.get('addtags'):
        for tag in parse_tag_input(request.POST.get('tags')):
            newtag = Tag(name= tag)
            newtag.save()
    
    context['pythonv'] = sys.version
    context['djangov'] = django.VERSION
    context['tags'] = Tag.objects.all()
    context['activePledgeCount'] = Pledge.objects.campaign_active().count()
    return render(request, 'main/settings.html', context)


def report(request):
    
    context = {}
    daySummary = OrderedDict()
    localtz = pytz.timezone( settings.TIME_ZONE ) # https://stackoverflow.com/questions/24710233/python-convert-time-to-utc-format
    campaignid = 0
    
    if request.user.is_authenticated:
        context['campaigns'] = get_campaigns()
    
    if request.GET.get('campaignid') and request.user.is_authenticated:
        campaignid = int(request.GET.get('campaignid'))
        campaign = Campaign.objects.get(pk=campaignid)
        context['campaign_name'] = campaign.name
        days = Pledge.objects.campaign_past_id( campaignid ).datetimes('create_date', 'day', 'DESC', localtz)
    else:
        days = Pledge.objects.campaign_active().datetimes('create_date', 'day', 'DESC', localtz)
        
    dayDetail = request.GET.get('dayDetail', None)
    
    for day in days:       
        label = calendar.day_name[day.weekday()] + ", " + str(day.month) + "/" + str(day.day) + "/" + str(day.year)
        
        if campaignid > 0:
            entries = Pledge.objects.campaign_past_id( campaignid ).filter(create_date__date=datetime.datetime(day.year, day.month, day.day, 0,0, tzinfo=localtz)).order_by('create_date') 
        else:
            entries = Pledge.objects.campaign_active().filter(create_date__date=datetime.datetime(day.year, day.month, day.day, 0,0, tzinfo=localtz)).order_by('create_date')
        
        count = entries.count()
        
        if dayDetail == day.date().__str__():
            context['date'] = datetime.date(day.year, day.month, day.day)
            context['hourlyBreakdown'] = hourlyBreakdown(entries)
                        
        daySummary[day.date().__str__()] = {
            'dayDetail': day.date().__str__(), 
            'label': label, 
            'count': count, 
            'summaryData': get_summaryData(label, entries, None)
        }
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
        hrlyids = []
        for entry in matches:
            hrlyids.append(entry.id)
        qs = Pledge.objects.all().filter(id__in=hrlyids)
        
        createdate = entry.create_date
        timestring = createdate.astimezone( pytz.timezone( settings.TIME_ZONE ))
        
        label = group + " Breakdown for " + timestring.strftime("%b %d, %Y") 

        hbd[group] = {'count': len(hrlyids), 'summaryData': get_summaryData(label, qs, None), 'entries': qs}
         
    return hbd


import pickle
def encode_entries(entries):
    entry_queryset_pickle = pickle.dumps(entries.query)
    encoded_pickle = urlsafe_b64encode(entry_queryset_pickle)
    return encoded_pickle


def decode_entries(encoded_pickle):
    # Updating Python to 3.7 introduced issues with urlsafe_b64decode when decoding the string we will see here.  
    # Our incoming URL list variable looks like b'<stuff>'
    # taking out the b' and closing ' gives us something we can work with and avoids errors like:
    #   pickle.UnpicklingError: invalid load key, 'n'.
    #   binascii.Error: Invalid base64-encoded string: length cannot be 1 more than a multiple of 4
    encoded_pickle = encoded_pickle[2:-1]
    
    entry_queryset_pickle = urlsafe_b64decode(encoded_pickle) 
    entry_queryset = pickle.loads(entry_queryset_pickle)
    entries = Pledge.objects.all()
    entries.query = entry_queryset
    
    return entries
             

from django.db.utils import OperationalError  
def get_taglist(entries, topnum):
    
    bool(entries) # will see issues working with the queryset without this 
    taglist = OrderedDict()
    
    if entries == None:
        entries = Pledge.objects.all()
    
    try:
        tags = Tag.objects.usage_for_queryset(entries, counts=True, min_count=None)
        tags.sort(key=lambda x: x.count, reverse=True)
        
        for tag in tags:
            tagged = TaggedItem.objects.get_by_model(entries, tag)       
            taglist[tag.count.__str__() + "-" + tag.name] = tag.name, tagged.aggregate(Sum('amount'))['amount__sum'], encode_entries(tagged)
        
        if topnum != None:
            int(topnum)
            while len(taglist) > topnum:
                taglist.popitem()
            
        return taglist
    
    except OperationalError: 
        # re-author entries by id versus tags as the OperationalError here should be:
        #  django.db.utils.OperationalError: ambiguous column name: tagging_taggeditem.content_type_id
        #
        # Example of broken query from an entries queryset that causes this exception (for future rainy days or bug fixing)
        # the query:
        # SELECT "main_pledge"."id", "main_pledge"."amount", "main_pledge"."firstname", "main_pledge"."lastname", "main_pledge"."is_first_time_donor", "main_pledge"."is_thanked", "main_pledge"."is_monthly", "main_pledge"."create_date", "main_pledge"."station_id", "main_pledge"."city", "main_pledge"."comment" FROM "main_pledge" , "tagging_taggeditem" , "tagging_taggeditem" WHERE (("tagging_taggeditem".content_type_id = 2) AND ("tagging_taggeditem".tag_id = 5) AND ("main_pledge"."id" = "tagging_taggeditem".object_id) AND ("tagging_taggeditem".content_type_id = 2) AND ("tagging_taggeditem".tag_id = 5) AND ("main_pledge"."id" = "tagging_taggeditem".object_id))
        #
        # a pickle of the query:
        # b'\x80\x03cdjango.db.models.sql.query\nQuery\nq\x00)\x81q\x01}q\x02(X\x05\x00\x00\x00modelq\x03cmain.models\nPledge\nq\x04X\x0e\x00\x00\x00alias_refcountq\x05}q\x06(X\x0b\x00\x00\x00main_pledgeq\x07K\x00X\x12\x00\x00\x00tagging_taggeditemq\x08K\x01uX\t\x00\x00\x00alias_mapq\tccollections\nOrderedDict\nq\n)Rq\x0bh\x07cdjango.db.models.sql.datastructures\nBaseTable\nq\x0c)\x81q\r}q\x0e(X\n\x00\x00\x00table_nameq\x0fh\x07X\x0b\x00\x00\x00table_aliasq\x10h\x07ubsX\x10\x00\x00\x00external_aliasesq\x11cbuiltins\nset\nq\x12]q\x13\x85q\x14Rq\x15X\t\x00\x00\x00table_mapq\x16}q\x17(h\x07]q\x18h\x07ah\x08]q\x19h\x08auX\x0c\x00\x00\x00default_colsq\x1a\x88X\x10\x00\x00\x00default_orderingq\x1b\x88X\x11\x00\x00\x00standard_orderingq\x1c\x88X\x06\x00\x00\x00selectq\x1d]q\x1eX\x06\x00\x00\x00tablesq\x1f]q (h\x07h\x08eX\x05\x00\x00\x00whereq!cdjango.db.models.sql.where\nWhereNode\nq")\x81q#}q$(X\x08\x00\x00\x00childrenq%]q&(cdjango.db.models.sql.where\nExtraWhere\nq\')\x81q(}q)(X\x04\x00\x00\x00sqlsq*]q+(X)\x00\x00\x00"tagging_taggeditem".content_type_id = %sq,X \x00\x00\x00"tagging_taggeditem".tag_id = %sq-X3\x00\x00\x00"main_pledge"."id" = "tagging_taggeditem".object_idq.eX\x06\x00\x00\x00paramsq/]q0(K\x02K\x05eubh\')\x81q1}q2(h*]q3(X)\x00\x00\x00"tagging_taggeditem".content_type_id = %sq4X \x00\x00\x00"tagging_taggeditem".tag_id = %sq5X3\x00\x00\x00"main_pledge"."id" = "tagging_taggeditem".object_idq6eh/]q7(K\x02K\x05eubeX\t\x00\x00\x00connectorq8X\x03\x00\x00\x00ANDq9X\x07\x00\x00\x00negatedq:\x89X\x12\x00\x00\x00contains_aggregateq;\x89ubX\x0b\x00\x00\x00where_classq<h"X\x08\x00\x00\x00group_byq=NX\x08\x00\x00\x00order_byq>]q?X\x08\x00\x00\x00low_markq@K\x00X\t\x00\x00\x00high_markqANX\x08\x00\x00\x00distinctqB\x89X\x0f\x00\x00\x00distinct_fieldsqC]qDX\x11\x00\x00\x00select_for_updateqE\x89X\x18\x00\x00\x00select_for_update_nowaitqF\x89X\x1d\x00\x00\x00select_for_update_skip_lockedqG\x89X\x0e\x00\x00\x00select_relatedqH\x89X\r\x00\x00\x00values_selectqI]qJX\x0c\x00\x00\x00_annotationsqKNX\x16\x00\x00\x00annotation_select_maskqLNX\x18\x00\x00\x00_annotation_select_cacheqMNX\t\x00\x00\x00max_depthqNK\x05X\n\x00\x00\x00combinatorqONX\x0e\x00\x00\x00combinator_allqP\x89X\x10\x00\x00\x00combined_queriesqQ)X\x06\x00\x00\x00_extraqRNX\x11\x00\x00\x00extra_select_maskqSNX\x13\x00\x00\x00_extra_select_cacheqTNX\x0c\x00\x00\x00extra_tablesqUh\x08X\x12\x00\x00\x00tagging_taggeditemqV\x86qWX\x0e\x00\x00\x00extra_order_byqX)X\x10\x00\x00\x00deferred_loadingqYh\x12]qZ\x85q[Rq\\\x88\x86q]X\x0c\x00\x00\x00used_aliasesq^h\x12]q_\x85q`RqaX\x10\x00\x00\x00filter_is_stickyqb\x89X\x08\x00\x00\x00subqueryqc\x89X\x07\x00\x00\x00contextqd}qeX\n\x00\x00\x00_forced_pkqf\x89ub.'
        
        idlist = [str(entry.id) for entry in entries]            
        entries = Pledge.objects.filter(id__in=idlist)
        
        # try again 
        taglist = get_taglist(entries, topnum)
        return taglist
     
    return None


def get_summaryData(label, entries, stations):
    
    if entries == None:
        entries = Pledge.objects.campaign_active().all()

    total_entries = encode_entries(entries)
    total_dollars = entries.aggregate(Sum('amount'))['amount__sum']
    total_pledges = entries.count()
    
    nd_entries = entries.filter(is_first_time_donor__exact=True)
    new_entries = encode_entries(nd_entries)
    new_donors = nd_entries.count()
    new_donor_dollars = nd_entries.aggregate(Sum('amount'))['amount__sum']
    
    md_entries = entries.filter(is_monthly__exact=True)
    monthly_entries = encode_entries(md_entries)
    monthly_donors = md_entries.count()
    monthly_dollars = md_entries.aggregate(Sum('amount'))['amount__sum']
    
    sd_entries = entries.filter(is_monthly__exact=False)
    single_entries = encode_entries(sd_entries)
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
    entries = decode_entries(request.GET.get('list'))
    
    label = request.GET.get('label')
    summaryData = get_summaryData(label, entries, Station.objects.all() )
    return render(request, 'main/entryListDetail.html', { 'label': label, 'summaryData': summaryData, 'entries': entries[:15] })
  


def deletePledgeEntry(request):
    if request.user.is_authenticated():
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
        
    else:
        return None

    
    
def editPledgeEntry(request):
  
    entries = Pledge.objects.campaign_active().order_by('-id')[:20]  # [::-1]
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
            p.is_anonymous = form.cleaned_data['is_anonymous']
            p.is_first_time_donor = form.cleaned_data['is_first_time_donor']
            p.is_monthly = form.cleaned_data['is_monthly']
            p.station = form.cleaned_data['station']
            p.phone_number = form.cleaned_data['phone_number']
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
        form.fields["is_anonymous"].initial = p.is_anonymous
        form.fields["is_monthly"].initial = p.is_monthly
        form.fields["is_first_time_donor"].initial = p.is_first_time_donor
        form.fields["station"].initial = p.station
        form.fields["phone_number"].initial = p.phone_number
        form.fields["tags"].initial = tags
        form.fields["comment"].initial = p.comment
        
    return render(request, 'main/pledgeEntry.html', { 'form': form, 'entryid': entryid, 'entryObject': p, 'entries': entries })



def bumpPledgeTime(request):
    entryid = int_or_0(request.GET.get('entryid'))
    direction = request.GET.get('direction')
    mins = int_or_0(request.GET.get('mins'))
    
    p = Pledge.objects.get(pk=entryid)
    
    if direction == 'back':
        p.create_date = p.create_date - timedelta(minutes=mins)
        p.save()
    elif direction == 'forward':
        p.create_date = p.create_date + timedelta(minutes=mins)
        p.save()
    else:
        pass
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def pledgeEntry(request):
    
    entries = Pledge.objects.campaign_active().order_by('-id')[:20]  # [::-1]
    
    form = PledgeEntryForm(request.POST or None)
    
    if form.is_valid():
    
        entry = Pledge(
            firstname=form.cleaned_data['firstname'],
            lastname=form.cleaned_data['lastname'],
            city=form.cleaned_data['city'],
            amount=form.cleaned_data['amount'],
            is_anonymous = form.cleaned_data['is_anonymous'],
            is_first_time_donor=form.cleaned_data['is_first_time_donor'],
            is_monthly=form.cleaned_data['is_monthly'],
            station=form.cleaned_data['station'],
            phone_number=form.cleaned_data['phone_number'],
            comment=form.cleaned_data['comment'],
            )

        # tags are special.  Have to have an entry before we can tag it.
        entry.save()
        entry.tags = form.cleaned_data['tags']

        # Auto-add Apostle tag on entries that are 1000+ on entry
        if entry.amount > 999:
            tags = 'Apostle, '
            for tag in list(entry.tags.values_list('name', flat=True)):
                tags += tag + ', '
            entry.tags = tags
                
        # Auto-add BTC tag when firstname and lastname are blank
        if not entry.firstname: 
            if not entry.lastname:
                tags = 'BTC, '
                for tag in list(entry.tags.values_list('name', flat=True)):
                    tags += tag + ', '
            entry.tags = tags
        
        entry.save()
        
        form = PledgeEntryForm(None)
        entries = Pledge.objects.campaign_active().order_by('-id')[:20]  # [::-1]
        return HttpResponseRedirect('/pledgeEntry/')
    
    if request.GET.get('getrandom', None):
        myform = getRandomPledgeForm()
        form.fields["firstname"].initial = myform.firstname
        form.fields["lastname"].initial = myform.lastname
        form.fields["city"].initial = myform.city
        form.fields["amount"].initial = myform.amount
        form.fields["is_anonymous"].initial = myform.is_anonymous
        form.fields["is_first_time_donor"].initial = myform.is_first_time_donor
        form.fields["is_monthly"].initial = myform.is_monthly
        form.fields["station"].initial = myform.station
        form.fields["phone_number"].initial = myform.phone_number
        form.fields["tags"].initial = myform.tags
        form.fields["comment"].initial = myform.comment

    return render(request, 'main/pledgeEntry.html', { 'form': form, 'entries': entries })
