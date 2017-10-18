#import datetime
from django.utils import timezone

from django.db import models
from tagging.registry import register


class TrackathonSetting(models.Model):
    name = models.CharField(max_length=50)
    enabled = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.name) + ": " + str(self.enabled)
    

class Station(models.Model):
    name = models.CharField(max_length=200)
    callsign = models.CharField(max_length=4)
    
    def __str__(self):
        return str(self.callsign) + ": " + str(self.name)
    

class Pledge(models.Model):

    amount = models.DecimalField(max_digits=9,decimal_places=2)
    firstname = models.CharField(max_length=35)
    lastname = models.CharField(max_length=35)
    is_first_time_donor = models.BooleanField(default=False)
    is_thanked = models.BooleanField(default=False)
    is_monthly = models.BooleanField(default=False)
    create_date = models.DateTimeField(default=timezone.now)
    station = models.ForeignKey(Station, on_delete=models.PROTECT, null=True)
    city = models.CharField(max_length=35)
    comment = models.TextField()

    def __str__(self):
        title = "$"+str(self.amount) +" - "+ self.firstname +" "+ self.lastname
        if self.is_monthly:
            title = title + " - Monthly"
        if self.is_first_time_donor:
            title = title + " - FirstTimeDonor"
        if not self.is_thanked:
            title = title + " - Not Thanked"
        return  title
    
register(Pledge)












