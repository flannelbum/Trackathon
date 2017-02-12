# http://stackoverflow.com/questions/3540288/how-do-i-read-a-random-line-from-one-file-in-python

import random
from django.conf import settings
from main.forms import PledgeEntryForm

def getRandomPledgeForm():
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
