from base64 import urlsafe_b64encode, urlsafe_b64decode
import calendar
from collections import OrderedDict
import datetime
from datetime import datetime as dt, timedelta
import itertools

from django.conf import settings
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
import pytz
from tagging.models import Tag, TaggedItem

from main.customFunctions import getRandomPledgeForm, int_or_0, autotag
from main.forms import PledgeEntryForm
from main.models import Pledge, Station, Campaign
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from main.GoalTender import get_goal

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
#         context['overall_totals_summaryData'] = get_summaryData( "Campaign Overall", Pledge.objects.campaign_active().all(), None )
        
        # get latest entry
        latestentry = Pledge.objects.campaign_active().all().latest('create_date')
        context['lid'] = latestentry.id
        context['goal_overall'] = get_goal(goal_datetime=latestentry.create_date)
        
        # get all entries in the same day as latest
        day_entries = Pledge.objects.campaign_active().filter(create_date__date=( latestentry.create_date ))
        context['latest_day_summaryData'] = get_summaryData( "Current Day", day_entries, None)
        context['latest_day_hourlyBreakdownHREFLink'] = '/hourlyBreakdown/?label=Today&list=' + str(encode_entries(day_entries))
        context['goal_daily'] = get_goal('daily', goal_datetime=latestentry.create_date)
        
        # all entries for the latest hour
        latest_entries = get_entries_in_same_hour_as(latestentry)
        context['latest_hour_summaryData'] = get_summaryData( "Current Hour", latest_entries, None) 
        context['goal_hourly'] = get_goal('hourly', goal_datetime=latestentry.create_date)
        
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
            context['goal_previous_hourly'] = get_goal('hourly', goal_datetime=previous_entry.create_date)
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
  
  
from platform import python_version
from django import get_version
@login_required(login_url='/login/')
def TATsettings(request):

    context = {}

    if request.POST.get('logout'):
        logout(request)
        return redirect('dashboard')
    
    alert = ""
    message = ""
    start_date = None
    end_date = None
    if request.POST.get('start_date') or request.POST.get('end_date'):
               
        try:
            start_date = dt.strptime(request.POST.get('start_date'), '%m/%d/%Y')
            end_date = dt.strptime(request.POST.get('end_date'), '%m/%d/%Y')

            if start_date > end_date:
                alert = "Start date must be before end date"
            else:
                message = "Start date set: " + dt.strftime(start_date, '%m/%d/%Y') + " End date set: " + dt.strftime(end_date, '%m/%d/%Y')
                Pledge.objects.set_active_campaign_start_date(start_date)
                Pledge.objects.set_active_campaign_end_date(end_date)
                
        except ValueError:        
            alert = "Invalid date(s) selected"
    
    else:
        ## get the start and end date from the database if exists
        start_date = Pledge.objects.get_active_campaign_start_date()
        end_date = Pledge.objects.get_active_campaign_end_date()
    
    if start_date != None: 
        context['start_date'] = dt.strftime(start_date, '%m/%d/%Y')
    else: 
        context['start_date'] = start_date
    
    if end_date != None:
        context['end_date'] = dt.strftime(end_date, '%m/%d/%Y')
    else:
        context['end_date'] = end_date
    
    
    if request.POST.get('new_campaign_name'):
        new_campaign = request.POST.get('new_campaign_name')    
        campaign = Campaign.objects.create(name=new_campaign)
        campaign.start_date = Pledge.objects.get_active_campaign_start_date()
        campaign.end_date = Pledge.objects.get_active_campaign_end_date()
        campaign.save()
        Pledge.objects.set_active_campaign_start_date(None)
        Pledge.objects.set_active_campaign_end_date(None)
        for pledge in Pledge.objects.campaign_active():
            pledge.campaign = campaign
            pledge.save()
        # TODO: Loop through and set campaign for Goal, GivingLevel, GiftAttribute, and GiftOption objects  
        return redirect('/report/?campaignid=' + str(campaign.id))
    
    
    context['alert'] = alert
    context['message'] = message  
    context['pythonv'] = python_version()  
    context['djangov'] = get_version()
    context['activePledgeCount'] = Pledge.objects.campaign_active().count()
    return render(request, 'main/settings.html', context)

import warnings
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
        fullSummary = Pledge.objects.campaign_past_id( campaignid ).all()
        
        start_date = Pledge.objects.get_past_campaign_start_date(campaignid)
        end_date = Pledge.objects.get_past_campaign_end_date(campaignid)
        context['start_date'] = start_date
        context['end_date'] = end_date

        if start_date != None and end_date != None:

            # Catch RuntimeWarning: DateTimeField Pledge.create_date received a naive datetime while time zone support is active.
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                preSummary = Pledge.objects.campaign_past_id( campaignid ).all().filter(create_date__range=('1970-01-01', start_date))
                midSummary = Pledge.objects.campaign_past_id( campaignid ).all().filter(create_date__range=(start_date, end_date + datetime.timedelta(days=1)))
                postSummary = Pledge.objects.campaign_past_id( campaignid ).all().filter(create_date__range=(end_date, '2100-01-01'))
                
            context['preSummary'] = get_summaryData("Pre-Sharathon Dollars", preSummary, None)
            context['preSlug'] = "Before " + datetime.datetime.strftime(start_date, '%m/%d/%Y')
            context['midSummary'] = get_summaryData("Sharathon Dollars", midSummary, None)
            context['midSlug'] = "Between " + datetime.datetime.strftime(start_date, '%m/%d/%Y') + " - " + datetime.datetime.strftime(end_date, '%m/%d/%Y')
            context['postSummary'] = get_summaryData("Post-Sharathon Dollars", postSummary, None)
            context['postSlug'] = "After " + datetime.datetime.strftime(end_date, '%m/%d/%Y')
    else:

        context['campaign_name'] = "Active Campaign"
        days = Pledge.objects.campaign_active().datetimes('create_date', 'day', 'DESC', localtz)
        fullSummary = Pledge.objects.campaign_active().all()
        
        start_date = Pledge.objects.get_active_campaign_start_date()
        end_date = Pledge.objects.get_active_campaign_end_date()
        context['start_date'] = start_date
        context['end_date'] = end_date
        if start_date != None and end_date != None:
            # Catch RuntimeWarning: DateTimeField Pledge.create_date received a naive datetime while time zone support is active.
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                preSummary = Pledge.objects.campaign_active().all().filter(create_date__range=('1970-01-01', start_date))
                midSummary = Pledge.objects.campaign_active().all().filter(create_date__range=(start_date, end_date + datetime.timedelta(days=1)))
                postSummary = Pledge.objects.campaign_active().all().filter(create_date__range=(end_date + datetime.timedelta(days=1), '2100-01-01'))
            
            context['preSummary'] = get_summaryData("Pre-Sharathon Dollars", preSummary, None)
            context['preSlug'] = "Before " + datetime.datetime.strftime(start_date, '%m/%d/%Y')
            context['midSummary'] = get_summaryData("Sharathon Dollars", midSummary, None)
            context['midSlug'] = "Between " + datetime.datetime.strftime(start_date, '%m/%d/%Y') + " - " + datetime.datetime.strftime(end_date, '%m/%d/%Y')
            context['postSummary'] = get_summaryData("Post-Sharathon Dollars", postSummary, None)
            context['postSlug'] = "After " + datetime.datetime.strftime(end_date, '%m/%d/%Y')
    
    
    context['fullSummary'] = get_summaryData("Grand Total Overall", fullSummary, None, 15)
    
    for day in days:
        formattedDate = calendar.day_name[day.weekday()] + ", " + str(day.month) + "/" + str(day.day) + "/" + str(day.year)
        label = context['campaign_name'] + " » " + formattedDate
           
        if campaignid > 0:
            entries = Pledge.objects.campaign_past_id( campaignid ).filter(create_date__date=datetime.datetime(day.year, day.month, day.day, 0,0, tzinfo=localtz)).order_by('create_date') 
        else:
            entries = Pledge.objects.campaign_active().filter(create_date__date=datetime.datetime(day.year, day.month, day.day, 0,0, tzinfo=localtz)).order_by('create_date')
           
        count = entries.count()
        encoded_dayEntries = encode_entries(entries)
                           
        daySummary[day.date().__str__()] = {
            'dayDetail': day.date().__str__(), 
            'label': label, 
            'count': count,
            'formattedDate': formattedDate,
            'encoded_dayEntries': encoded_dayEntries
        }
        
    context['daySummary'] = daySummary
      
    return render(request, 'main/report.html', context)
   
    
def hourlyBreakdownPage(request):
    context = {}
    entries = decode_entries(request.GET.get('list'))
    context['label'] = request.GET.get('label')
    context['summaryData'] = get_summaryData(context['label'], entries, Station.objects.all(), 'ALL' )
    context['hourlyBreakdown'] = hourlyBreakdown(entries)
    return render(request, 'main/hourlyBreakdown.html', context)

    
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
        
        label = group + timestring.strftime(" %A, %b %d, %Y") 

        hbd[group] = {'count': len(hrlyids), 'summaryData': get_summaryData(label, qs, None, 'ALL'), 'entries': qs}
         
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


def get_summaryData(label, entries, stations=None, number_of_tags=None):
    
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
  
    stationData = {}
    if stations:
        for station in stations:
            station_entries = entries.filter(station=station)
            if station_entries.count() > 0:
                stationData[station.callsign + " / " + station.name] = get_summaryData(None, station_entries, None)  

    if number_of_tags == 'ALL':
        tags = get_taglist(entries, None)
    elif number_of_tags != None:
        tags = get_taglist(entries, number_of_tags)
    else:
        tags = get_taglist(entries, 5)
    
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
        'stationData': stationData,
        'tags': tags,
    }

    return summaryData

  
def entryListDetail(request):
    entries = decode_entries(request.GET.get('list'))
    
    label = request.GET.get('label')
    summaryData = get_summaryData(label, entries, Station.objects.all(), 'ALL' )
    return render(request, 'main/entryListDetail.html', { 'label': label, 'summaryData': summaryData, 'entries': entries[:15] })
  


def deletePledgeEntry(request):
    if request.user.is_authenticated:
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
                        
            p.firstname = form.clean_firstname()
            p.lastname = form.clean_lastname()
            p.address1 = form.clean_address1()
            p.address2 = form.clean_address2()
            p.city = form.clean_city()
            p.state = form.clean_state()
            p.zip = form.cleaned_data['zip']
            p.amount = form.cleaned_data['amount']
            p.is_anonymous = form.cleaned_data['is_anonymous']
            p.is_first_time_donor = form.cleaned_data['is_first_time_donor']
            p.is_monthly = form.cleaned_data['is_monthly']
            p.station = form.cleaned_data['station']
            p.phone_number = form.cleaned_data['phone_number']
            p.tags = form.clean_tags()
            p.comment = form.clean_comment()
            p.save()
            form = PledgeEntryForm(None)
            return HttpResponseRedirect('/pledgeEntry/')
      
    else:
        
        taglist = list(p.tags.values_list('name', flat=True))
        tags = ", ".join(taglist) 
        
        form = PledgeEntryForm(None)
        form.fields["firstname"].initial = p.firstname
        form.fields["lastname"].initial = p.lastname
        form.fields["address1"].initial = p.address1
        form.fields["address2"].initial = p.address2
        form.fields["city"].initial = p.city
        form.fields["state"].initial = p.state
        form.fields["zip"].initial = p.zip
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
            firstname=form.clean_firstname(),
            lastname=form.clean_lastname(),
            address1=form.clean_address1(),
            address2=form.clean_address2(),
            city=form.clean_city(),
            state=form.clean_state(),
            zip=form.cleaned_data['zip'],
            amount=form.cleaned_data['amount'],
            is_anonymous = form.cleaned_data['is_anonymous'],
            is_first_time_donor=form.cleaned_data['is_first_time_donor'],
            is_monthly=form.cleaned_data['is_monthly'],
            station=form.cleaned_data['station'],
            phone_number=form.cleaned_data['phone_number'],
            comment=form.clean_comment(),
            )

        # tags are special.  Have to have an entry before we can tag it.
        entry.save()
        entry.tags = form.clean_tags()
                       
        # save entry so it has its user-submitted tags before we throw it through autotag which will also save the entry
        entry.save()
        autotag(entry)
        
        form = PledgeEntryForm(None)
        form.fields["state"].initial = "OH"

        return HttpResponseRedirect('/pledgeEntry/')
            
    
    if request.GET.get('getrandom', None):
        myform = getRandomPledgeForm()
        form.fields["firstname"].initial = myform.firstname
        form.fields["lastname"].initial = myform.lastname
        form.fields["address1"].initial = myform.address1
        form.fields["address2"].initial = myform.address2
        form.fields["city"].initial = myform.city
        form.fields["state"].initial = myform.state
        form.fields["zip"].initial = myform.zip
        form.fields["amount"].initial = myform.amount
        form.fields["is_anonymous"].initial = myform.is_anonymous
        form.fields["is_first_time_donor"].initial = myform.is_first_time_donor
        form.fields["is_monthly"].initial = myform.is_monthly
        form.fields["station"].initial = myform.station
        form.fields["phone_number"].initial = myform.phone_number
        form.fields["tags"].initial = myform.tags
        form.fields["comment"].initial = myform.comment

    return render(request, 'main/pledgeEntry.html', { 'form': form, 'entries': entries })
