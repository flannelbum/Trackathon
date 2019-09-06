from django.utils import timezone

from django.db import models
from tagging.registry import register


class TATSettingManager(models.Manager):
    
    def getSetting(self, setting_name):
        try:
            setting = TATSetting.objects.get(setting=setting_name)
        except TATSetting.DoesNotExist:
            setting = TATSetting(setting=setting_name, value=None, date=None)
            setting.save()
        return setting
    
    def setSetting(self, setting_name, setting_value, setting_date):
        try:
            setting = TATSetting.objects.get(setting=setting_name)
        except TATSetting.DoesNotExist:
            setting = TATSetting(setting=setting_name, value=None, date=None)
            
        setting.value = setting_value
        setting.date = setting_date
        setting.save()
        return setting
    
    def deleteSetting(self, setting_name):
        try:
            setting = TATSetting.objects.get(setting=setting_name)
            setting.delete()
        except TATSetting.DoesNotExist:
            pass


class TATSetting(models.Model):
    setting = models.CharField(max_length=200, unique=True, blank=False, null=False)
    value = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateField(default=None, blank=True, null=True) 
    
    def __str__(self):
        return self.setting + ' - ' + str(self.value) + ' - ' + str(self.date)
    
    objects = TATSettingManager()



class Campaign(models.Model):
    name = models.CharField(max_length=200)
    start_date = models.DateField(default=None, blank=True, null=True)
    end_date = models.DateField(default=None, blank=True, null=True)
    
    def __str__(self):
        return str(self.name)
        
        
class Station(models.Model):
    name = models.CharField(max_length=200)
    callsign = models.CharField(max_length=4)
    
    def __str__(self):
        return str(self.callsign) + ": " + str(self.name)
    

class PledgeCampaign(models.Manager):
    
    def campaign_active(self):
        return super().get_queryset().filter(campaign__exact=None)

    def campaign_past_id(self, campaign_id):
        campaign = Campaign.objects.get(id=campaign_id)
        return super().get_queryset().filter(campaign__exact=campaign)
    
    def get_active_campaign_start_date(self):
        return TATSetting.objects.getSetting('activeCampaign_start_date').date
    
    def get_active_campaign_end_date(self):
        return TATSetting.objects.getSetting('activeCampaign_end_date').date
        
    def set_active_campaign_start_date(self, start_date):
        TATSetting.objects.setSetting('activeCampaign_start_date', None, start_date)
            
    def set_active_campaign_end_date(self, end_date):
        TATSetting.objects.setSetting('activeCampaign_end_date', None, end_date) 
    
    def get_past_campaign_start_date(self, campaign_id):
        campaign = Campaign.objects.get(id=campaign_id)
        return campaign.start_date
        
    def get_past_campaign_end_date(self, campaign_id):
        campaign = Campaign.objects.get(id=campaign_id)
        return campaign.end_date


class Pledge(models.Model):

    amount = models.DecimalField(max_digits=9,decimal_places=2)
    firstname = models.CharField(max_length=35, default=None)
    lastname = models.CharField(max_length=35, default=None)
    is_anonymous = models.BooleanField(default=False)
    is_first_time_donor = models.BooleanField(default=False)
    is_thanked = models.BooleanField(default=False)
    is_monthly = models.BooleanField(default=False)
    create_date = models.DateTimeField(default=timezone.now)
    station = models.ForeignKey(Station, on_delete=models.PROTECT, null=True)
    city = models.CharField(max_length=35, default=None)
    phone_number = models.CharField(max_length=13, blank=True)
    comment = models.TextField(default=None)
    campaign = models.ForeignKey(Campaign, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        title = "$"+str(self.amount) +" - "+ self.firstname +" "+ self.lastname
        if self.is_monthly:
            title = title + " - Monthly"
        if self.is_first_time_donor:
            title = title + " - FirstTimeDonor"
        if not self.is_thanked:
            title = title + " - Not Thanked"
        return  title
    
    objects = PledgeCampaign()
    
register(Pledge)
