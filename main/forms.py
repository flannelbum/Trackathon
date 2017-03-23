from django import forms
from main.models import PledgeEntry
from django.forms.widgets import RadioSelect, TextInput, CheckboxInput

# class TestForm(forms.Form):

class PledgeEntryForm(forms.Form):

    firstname = forms.CharField(
        max_length=35,
        widget=TextInput(
            attrs={'autocomplete':'off'}
        ),
        label='First Name',
    )


    lastname = forms.CharField(
        max_length=35,
        widget=TextInput(
            attrs={'autocomplete':'off'}
        ),
        label='Last Name',
    )


    city = forms.CharField(
        max_length=35,
        widget=TextInput(
            attrs={'autocomplete':'off'}
        ),
        label='City',
    )
    
    
    ftdonor = forms.BooleanField(
        required=False,
        widget=CheckboxInput(),
        #     choices=PledgeEntry.BOOL_CHOICES
        # ),
        label='First Time Donor',
    )


    # ftdonor = forms.BooleanField(
    #     required=False,
    #     widget=RadioSelect(
    #         choices=PledgeEntry.BOOL_CHOICES
    #     ),
    #     label='First Time Donor',
    # )


    # beenthanked = forms.BooleanField(
    #     required=False,
    #     widget=RadioSelect(
    #         choices=PledgeEntry.BOOL_CHOICES
    #     ),
    #     label='Has been thanked',
    # )


    amount = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        label='Amount',
    )


    singleormonthly = forms.ChoiceField(
        widget=forms.RadioSelect(
            attrs={'style': 'list-style-type: none;'}
        ),
        choices=PledgeEntry.ONETIMEORMONTHLY_CHOICES,
        label='Single or Monthly',
    )


    callsign = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={'style': 'list-style-type: none;'}),
        # widget=forms.RadioSelect(attrs={'class': 'classy'}),
        choices=PledgeEntry.STATION_CHOICES,
        # attrs={'style': 'list-style: none;'},
        label='Station',
    )


    parish = forms.CharField(
        max_length=100,
        widget=TextInput(
            attrs={'autocomplete':'off'}
        ),
        label='Parish',
    )


    groupcallout = forms.CharField(
        required=False,
        max_length=100,
        widget=TextInput(
            attrs={'autocomplete':'off'}
        ),
        label='Group Call-Out',
    )


    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={'autocomplete':'off'}
        ),
        label='Comments',
    )
