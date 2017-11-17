from datetime import datetime
from pytz import timezone

from random import choice, randint, sample

from django.conf import settings
from django.utils import lorem_ipsum

from main.forms import PledgeEntryForm
from main.models import Pledge, Station
from tagging.models import Tag



def int_or_0(value):
    # Helper function to return an integer for a given value (string)
    #  if none found, return 0
    try:
        return int(value)
    except:
        return 0 


def getRandomPledgeForm():
    form = PledgeEntryForm()
    entry = generateRandomPledge(None, False)
    
    form.firstname = entry['firstname']
    form.lastname = entry['lastname']
    form.city = entry['city']
    form.is_first_time_donor = entry['is_first_time_donor']
    form.is_monthly = entry['is_monthly']
    form.amount = entry['amount']
    form.station = entry['station']
    form.phone_number = entry['phone_number']
    form.tags = entry['tags']
    form.comment = entry['comment']
    
    return form

    
    
def generateRandomPledge(date, create_entry):
    
    if date == None:
        date = datetime.now()
    
    # Pool of values
    firstnames = ['John', 'Paul', 'George', 'Ringo', 'Christopher', 'David', 'Jane', 'Julia', 'Prudence', 'Cindy', 'Marge', 'Homer', 'Bart', 'Lisa', 'Maggie', 'Donna', 'Ron', 'Sean', 'Melanie', 'Colleen', 'Liam', 'Alan', 'Noel', 'Lilly', 'Mike', 'Terry', 'Jason', 'Jill', 'Tim']
    lastnames = ['Smith', 'Johnson', 'Davidson', 'Schwartz', 'Doe', 'Miller', 'Washington', 'Jefferson', 'Jones', 'Mayhew', 'Robertson', 'Dinkle', 'Westinghouse', 'Burns', 'Simpson', 'Harrison', 'Starr', 'McCartney', 'Lennon']
    cities = ['Toledo', 'Perrysburg', 'Maumee', 'Port Clinton', 'Wallbridge', 'Sylvania', 'Holland', 'Swanton', 'Millbury', 'Rossford', 'Northwood', 'Lime City', 'Monclova', 'Genoa', ]
   
    try:   
        tags = ",".join(sample(list(Tag.objects.all().values_list('name', flat=True)),2))
    except(ValueError):
        print('Tag issue.  No tags in system?')
        tags = ''

    entrydict = {
        'create_date': date,
        'firstname': str(choice(firstnames)),
        'lastname': str(choice(lastnames)),
        'city': str(choice(cities)),
        'amount': randint(1,70),
        'is_first_time_donor': choice([True, False]),
        'is_monthly': choice([True, False]),
        'station': choice(Station.objects.all()),
        'phone_number': '(419)555-' + str(choice(range(0000,9999))),
        'tags': tags,
        }
    entrydict['comment'] = 'Randomly generated comment for ' + entrydict['firstname'] + ' ' + entrydict['lastname'] + ': ' + lorem_ipsum.words(randint(5,75), False)
    
    if create_entry:
        # Generate entry            
        entry = Pledge(
            create_date = entrydict['create_date'],
            firstname = entrydict['firstname'],
            lastname = entrydict['lastname'],
            city = entrydict['city'],
            amount = entrydict['amount'],
            is_first_time_donor = entrydict['is_first_time_donor'],
            is_monthly = entrydict['is_monthly'],
            station = entrydict['station'],
            phone_number = entrydict['phone_number'],
            comment = entrydict['comment']
            )
        # tags are special.  Have to have an entry before we can tag it.
        entry.save()
        entry.tags = tags
        entry.save()
        
    return entrydict
        
        
        
def generateDay(year, month, day):
    localtz = timezone( settings.TIME_ZONE)
    for hour in range(5,20):
        for minute in range(0,60):
            generateRandomPledge(localtz.localize(datetime(year, month, day, hour, minute, 0)),True)


def getRandomPledgeForm_old():
    # http://stackoverflow.com/questions/3540288/how-do-i-read-a-random-line-from-one-file-in-python
    # firstname,lastname,city,ftdonor,beenthanked,amount,singleormonthly,callsign,parish,groupcallout,comment
    myfile = settings.BASE_DIR + '/main/static/main/randomData.csv'
    lines = open(myfile).read().splitlines()
    myline = choice(lines)

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
    
    
    
    
    
    
    
    
    
    
    

