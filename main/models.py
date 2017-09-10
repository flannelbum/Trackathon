from django.db import models

# Create your models here.


class Summary(models.Model):
    date = models.DateTimeField()
    totalamount = models.DecimalField( max_digits=9, decimal_places=2 )
    totalpledges = models.IntegerField()
    newdonors_count = models.IntegerField()
    newdonors_totaldollars = models.DecimalField( max_digits=9, decimal_places=2 )
    monthlydonors_count = models.IntegerField()
    monthlydonors_totaldollars = models.DecimalField( max_digits=9, decimal_places=2)
    singledonors_count = models.IntegerField()
    singledonors_totaldollars = models.DecimalField( max_digits=9, decimal_places=2)
  
  

class PledgeEntry(models.Model):

    BOOL_CHOICES = (
        (True, 'Yes'),
        (False, 'No'),
    )
    STATION_CHOICES = (
        ('WNOC', '89.7 WNOC Toledo-Bowling Green'),
        ('WHRQ', '88.1 WHRQ Sandusky-Port Clinton'),
        ('WFOT', '89.5 WFOT Mansfield-Lexington'),
        ('WSHB', '90.9 WSHB Willard-Shelby'),
        ('WRRO', '89.9 WRRO Edon-Bryan'),
        ('WLBJ', '104.1 WLBJ Fostoria'),
        ('WEB', 'Online/WEB'),
    )
    ONETIMEORMONTHLY_CHOICES = (
        ('single','Single'),
        ('monthly','Monthly'),
    )
    amount = models.DecimalField(max_digits=9,decimal_places=2)
    ftdonor = models.BooleanField(choices=BOOL_CHOICES,default=False )
    beenthanked = models.BooleanField(choices=BOOL_CHOICES,default=False )
    create_date = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    groupcallout = models.CharField(max_length=100)
    singleormonthly = models.CharField(
        max_length=10,
        choices=ONETIMEORMONTHLY_CHOICES,
        default='single'
        )
    callsign = models.CharField(
        max_length=4,
        choices=STATION_CHOICES
        )
    firstname = models.CharField(max_length=35)
    lastname = models.CharField(max_length=35)
    city = models.CharField(max_length=35)
    parish = models.CharField(max_length=100)

    def __str__(self):
        return "$"+str(self.amount) +": "+ self.firstname +" "+ self.lastname +" - "+ self.callsign + " FTD:" + str(self.ftdonor) + " TY:" + str(self.beenthanked)
