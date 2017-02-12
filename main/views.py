from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.paginator import Paginator
from main.forms import PledgeEntryForm
from main.models import PledgeEntry
from main.randomImport import getRandomPledgeForm
# Create your views here.


def index(request):
    entries = PledgeEntry.objects.all().order_by('-id')
    page = request.GET.get('page', 1)

    paginator = Paginator(entries, 15)
    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)

    return render(request, 'main/dashboard.html', { 'entries': entries })



def pledgeEntry(request):
    template_name='main/pledgeEntry.html'
    entries = PledgeEntry.objects.order_by('-id')[:10][::-1]

    form = PledgeEntryForm(request.POST or None)

    if form.is_valid():

        entry = PledgeEntry(
            firstname = form.cleaned_data['firstname'],
            lastname = form.cleaned_data['lastname'],
            city = form.cleaned_data['city'],
            ftdonor = form.cleaned_data['ftdonor'],
            beenthanked = form.cleaned_data['beenthanked'],
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
        form.fields["beenthanked"].initial = myform.beenthanked
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
