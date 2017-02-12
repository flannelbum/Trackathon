from django.shortcuts import render, redirect
from django.http import HttpResponse
from main.forms import PledgeEntryForm
from main.models import PledgeEntry

# Create your views here.


def index(request):
    template_name='main/dashboard.html'
    entries = PledgeEntry.objects.order_by('-id')[:10][::-1]
    context = { 'entries': reversed(entries) }
    return render(request,template_name,context)


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

    return render(
        request,
        template_name, {
            'form': form,
            'entries': reversed(entries),
        },

    )
