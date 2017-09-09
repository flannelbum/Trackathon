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
    def clean_firstname(self):
      return self.cleaned_data['firstname'].upper()



    lastname = forms.CharField(
        max_length=35,
        widget=TextInput(
            attrs={'autocomplete':'off'}
        ),
        label='Last Name',
    )
    def clean_lastname(self):
      return self.cleaned_data['lastname'].upper()



    city = forms.CharField(
        required = False,
        max_length=35,
        widget=TextInput(
            attrs={'autocomplete':'off'}
        ),
        label='City',
    )
    def clean_city(self):
      return self.cleaned_data['city'].upper()
  
    
    
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
        required = False,
        widget=forms.RadioSelect(
            attrs={'style': 'list-style-type: none;'}
        ),
        choices=PledgeEntry.ONETIMEORMONTHLY_CHOICES,
        label='Single or Monthly',
    )


    callsign = forms.ChoiceField(
        required = False,
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
    def clean_parish(self):
      return self.cleaned_data['parish'].upper()



    groupcallout = forms.CharField(
        required=False,
        max_length=100,
        widget=TextInput(
            attrs={'autocomplete':'off'}
        ),
        label='Group Call-Out',
    )
    def clean_groupcallout(self):
      return self.cleaned_data['groupcallout'].upper()



    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={'autocomplete':'off'}
        ),
        label='Comments',
    )
    def clean_comment(self):
      return self.cleaned_data['comment'].upper()
