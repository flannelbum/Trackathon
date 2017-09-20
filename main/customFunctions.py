import datetime
import random

from django.conf import settings

from main.forms import PledgeEntryForm
from main.models import Station


def int_or_0(value):
    # Helper function to return an integer for a given value (string)
    #  if none found, return 0
    try:
        return int(value)
    except:
        return 0 


def getRandomPledgeForm():
    # http://stackoverflow.com/questions/3540288/how-do-i-read-a-random-line-from-one-file-in-python
    # firstname,lastname,city,ftdonor,beenthanked,amount,singleormonthly,callsign,parish,groupcallout,comment
    myfile = settings.BASE_DIR + '/main/static/main/randomData.csv'
    lines = open(myfile).read().splitlines()
    myline =random.choice(lines)

    form = PledgeEntryForm()
    myline = myline.split(',')
    form.firstname = myline[0]
    form.lastname = myline[1]
    form.city = myline[2]
    
    # translate random data csv instead of rewritting it for now
    print( str(myline[3]) + " " + str(myline[6]))
    ml3 = False
    ml6 = False
    if str(myline[3]) == 'TRUE':
        ml3 = True
    if str(myline[6]) == 'monthly':
        ml6 = True
    
    form.is_first_time_donor = ml3
    form.is_monthly = ml6
    
    form.amount = myline[5]
    form.station = Station.objects.get(callsign=myline[7])
    form.comment = myline[10]
    
    return form


def prettydate(d):
    # http://stackoverflow.com/questions/410221/natural-relative-days-in-python
    diff = datetime.datetime.utcnow() - d
    s = diff.seconds
    if diff.days > 7 or diff.days < 0:
        return d.strftime('%d %b %y')
    elif diff.days == 1:
        return '1 day ago'
    elif diff.days > 1:
        return '{} days ago'.format(diff.days)
    elif s <= 1:
        return 'just now'
    elif s < 60:
        return '{} seconds ago'.format(s)
    elif s < 120:
        return '1 minute ago'
    elif s < 3600:
        return '{} minutes ago'.format(s/60)
    elif s < 7200:
        return '1 hour ago'
    else:
        return '{} hours ago'.format(s/3600)
