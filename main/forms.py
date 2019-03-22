from django import forms
from django.forms.widgets import TextInput, CheckboxInput
from tagging.forms import TagField
from tagging_autocomplete.widgets import TagAutocomplete

from main.models import Station


class PledgeEntryForm(forms.Form):
    
    
    amount = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        label='Amount',
    )
    
    is_anonymous = forms.BooleanField(
        required=False,
        widget=CheckboxInput(),
        label='Anonymous Pledge',
    )
    
    phone_number = forms.CharField(
        required=False,
        max_length=13,
        widget=TextInput(
            attrs={'autocomplete':'off'}
        ),
    )
    
    
    firstname = forms.CharField(
        required=True,
        max_length=35,
        widget=TextInput(
            attrs={'autocomplete':'off'}
        ),
        label='First Name',
    )
    def clean_firstname(self):
        return self.cleaned_data['firstname'].upper()


    lastname = forms.CharField(
        required=True,
        max_length=35,
        widget=TextInput(
            attrs={'autocomplete':'off'}
        ),
        label='Last Name',
    )
    def clean_lastname(self):
        return self.cleaned_data['lastname'].upper()
    
    
    city = forms.CharField(
        required=False,
        max_length=35,
        widget=TextInput(
            attrs={'autocomplete':'off'}
        ),
        label='City',
    )
    def clean_city(self):
        return self.cleaned_data['city'].upper()
  
    
    is_first_time_donor = forms.BooleanField(
        required=False,
        widget=CheckboxInput(),
        label='First Time Donor',
    )
    
    
    is_monthly = forms.BooleanField(
        required=False,
        widget=CheckboxInput(),
        label="Monthly Donation",        
    )


    station = forms.ModelChoiceField(
        required=False,
        queryset=Station.objects.all() 
    )
   
    
    tags = TagField( 
        required=False,
        widget=TagAutocomplete(
            attrs={'autocomplete':'off'}) )
    def clean_tags(self):
        # add a comma so spaced tags from form entry will be counted as a single tag
        tags = self.cleaned_data['tags'] + ','
        return tags
        
    
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={'autocomplete':'off'}
        ),
        label='Comments',
    )
    def clean_comment(self):
        return self.cleaned_data['comment'].upper()
