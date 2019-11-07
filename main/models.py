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


class Goal(models.Model):
    GOAL_TYPES = [
        ('overall','overall'),
        ('daily','daily'),
        ('hourly','hourly'),
        ]
    name = models.CharField(max_length=200, unique=False, blank=False, null=False)
    goal_type = models.CharField(max_length=7, choices=GOAL_TYPES, blank=False, null=False) 
    campaign = models.ForeignKey(Campaign, on_delete=models.PROTECT, null=True, blank=True)
    goal_amount = models.DecimalField(max_digits=9,decimal_places=2)
    raised_amount = models.DecimalField(max_digits=9,decimal_places=2)
    start_datetime = models.DateTimeField(default=None, blank=False, null=False)
    end_datetime = models.DateTimeField(default=None, blank=False, null=False) 
    
    def __str__(self):
        return self.goal_type + " goal - " + self.name + " (" + self.goal_percent() + "%) - $" + str(self.raised_amount) + " of $" + str(self.goal_amount)
    
    def goal_percent(self):
        return str(round( self.raised_amount / self.goal_amount * 100 ))
            
            
class GiftAttribute(models.Model):
    name = models.CharField(max_length=200)
    campaign = models.ForeignKey(Campaign, on_delete=models.PROTECT, null=True, blank=True)
    disable = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class GiftOption(models.Model):
    name = models.CharField(max_length=200, unique=False, blank=False, null=False)
    campaign = models.ForeignKey(Campaign, on_delete=models.PROTECT, null=True, blank=True)
    value = models.DecimalField(max_digits=9,decimal_places=2)
    attributes = models.ManyToManyField(GiftAttribute, blank=True)
    
    def has_attributes(self):
        if self.attributes.count() > 0:
            return True
        else:
            return False
    
    def __str__(self):
        return self.name
    
    
class GivingLevel(models.Model):
    name = models.CharField(max_length=200, unique=False, blank=False, null=False)
    campaign = models.ForeignKey(Campaign, on_delete=models.PROTECT, null=True, blank=True)
    low_amount = models.DecimalField(max_digits=9,decimal_places=2)
    high_amount = models.DecimalField(max_digits=9,decimal_places=2)
    tag = models.CharField(max_length=50, unique=False, blank=False, null=False)
    gift_option = models.ForeignKey(GiftOption, on_delete=models.PROTECT, null=True, blank=True)
    
    def has_gift_option(self):
        if self.gift_option:
            return True
        else:
            return False
    
    def __str__(self):
        return self.name + " ($" + str(self.low_amount) + " - $" + str(self.high_amount) + ")"
    
        
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
    thanked_datetime = models.DateTimeField(default=None, null=True, blank=True)
    is_monthly = models.BooleanField(default=False)
    create_date = models.DateTimeField(default=timezone.now)
    station = models.ForeignKey(Station, on_delete=models.PROTECT, null=True)
    address1 = models.CharField(max_length=100, default=None)
    address2 = models.CharField(max_length=100, default=None, null=True)
    city = models.CharField(max_length=35, default=None)
    state = models.CharField(max_length=2, default="OH")
    zip = models.CharField(max_length=5, default=None)
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


class Gift(models.Model):
    pledge = models.ForeignKey(Pledge, on_delete=models.CASCADE, blank=False, null=False)
    waived = models.BooleanField(default=False)
    is_fullfilled = models.BooleanField(default=False)
    gift = models.ForeignKey(GiftOption, on_delete=models.CASCADE, blank=False, null=False)
    attribute = models.ForeignKey(GiftAttribute, on_delete=models.CASCADE, blank=True, null=True)
    notes = models.TextField(default=None, null=True, blank=True)
    
    
