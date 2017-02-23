import random
import datetime
from django.conf import settings
from main.forms import PledgeEntryForm


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
    form.ftdonor = myline[3]
    form.beenthanked = myline[4]
    form.amount = myline[5]
    form.singleormonthly = myline[6]
    form.callsign = myline[7]
    form.parish = myline[8]
    form.groupcallout = myline[9]
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
