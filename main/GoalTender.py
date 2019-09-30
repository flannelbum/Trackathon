from main.models import Goal, Pledge
from django.utils import timezone
from django.db.models import Min, Max
import datetime
from django.conf import settings
import pytz

# returns single valid "overall" goal if defined
# returns single valid "daily" goal if defined for a given date or datetime object
# returns single valid "hourly" goal if defined for a given datetimee object

# updates all valid goal raised_amount totals for a given entry
#  - should be a single, "overall", "daily", and "hourly" goal if they have been defined
#  - is based on the given entry's thanked datetime
#  - Generate goals if none are defined for the given entry??
# recalculate a specific goal or all goals if none specified based on thanked datetime


def get_goal(goal_type=None, entry=None, goal_datetime=None, campaign=None):
    
    #goal_type must be specified otherwise "overall" is assumed
    if not any(goal_type in gtype for gtype in Goal.GOAL_TYPES):
        goal_type='overall'
    
    #try finding the most relevant goals per the goal_type and entry or entries given
#     if not entry and not goal_datetime:
#         return 
    
    if entry:     
        goal_datetime = entry.thanked_datetime
        campaign = entry.campaign
            
    if not goal_datetime:
        goal_datetime = timezone.now()
        
    try:
        if goal_type == 'overall':
            return Goal.objects.get(goal_type=goal_type, campaign=campaign)
        if goal_type == 'hourly':
            start_datetime = datetime.datetime.combine( goal_datetime.date(), datetime.time( goal_datetime.hour, 0, 0, 0, tzinfo=pytz.UTC))
            end_datetime = datetime.datetime.combine( start_datetime.date(), datetime.time( start_datetime.hour, 59, 59, 999999, tzinfo=pytz.UTC))
        elif goal_type == 'daily':
            start_datetime = datetime.datetime.combine( goal_datetime.date(), datetime.time( 0, 0, 0, 0, tzinfo=pytz.UTC))
            end_datetime = datetime.datetime.combine( start_datetime.date(), datetime.time( 23, 59, 59, 999999, tzinfo=pytz.UTC))
    
        goal = Goal.objects.get(goal_type__exact=goal_type, start_datetime__gte=start_datetime, end_datetime__lte=end_datetime, campaign__exact=campaign)
        
        return goal
    except Goal.DoesNotExist:
        return None



def get_goals(entry=None, goal_datetime=None):
    goals = []
    if entry:     
        goals.append(get_goal('overall', entry, goal_datetime=goal_datetime))
        goals.append(get_goal('daily', entry, goal_datetime=goal_datetime))
        goals.append(get_goal('hourly', entry, goal_datetime=goal_datetime))
    else:
        goals.append(get_goal('overall', None, goal_datetime=goal_datetime))
        goals.append(get_goal('daily', None, goal_datetime=goal_datetime))
        goals.append(get_goal('hourly', None, goal_datetime=goal_datetime))
    
    return goals


def update_goals(entry=None, amount=None, goal_datetime=None):
    if entry:     
        for goal in get_goals(entry):
            update_goal(goal, amount)
    else:
        for goal in get_goals(goal_datetime=goal_datetime):
            update_goal(goal, amount)


def update_goal(goal, amount):
    if goal:
        goal.raised_amount = goal.raised_amount + amount
        goal.save()
        

def set_goal(goal_type=None, entry=None, goal_datetime=None, name=None, goal_amount=None, raised_amount=None):
    #create a goal based on a passed in entry or type and datetime
    #always assume active campaign
    if not any(goal_type in gtype for gtype in Goal.GOAL_TYPES):
        goal_type='overall'
    
    if entry:
        if entry.thanked_datetime == None and goal_datetime==None:
            goal_datetime = timezone.now()
        if entry.thanked_datetime:
            goal_datetime = entry.thanked_datetime
    elif goal_datetime==None:
        goal_datetime = timezone.now()
    
    if goal_type == 'overall':
        start_datetime = goal_datetime
        end_datetime = goal_datetime
    elif goal_type == 'hourly':
        start_datetime = datetime.datetime.combine( goal_datetime.date(), datetime.time( goal_datetime.hour, 0, 0, 0, tzinfo=pytz.UTC))
        end_datetime = datetime.datetime.combine( start_datetime.date(), datetime.time( start_datetime.hour, 59, 59, 999999, tzinfo=pytz.UTC))
    elif goal_type == 'daily':
        start_datetime = datetime.datetime.combine( goal_datetime.date(), datetime.time( 0, 0, 0, 0, tzinfo=pytz.UTC))
        end_datetime = datetime.datetime.combine( start_datetime.date(), datetime.time( 23, 59, 59, 999999, tzinfo=pytz.UTC))

    if not name:
        name = datetime.datetime.strftime( start_datetime, '%m/%d/%Y %H:%M:%S' )
    
    if not get_goal(goal_type, None, goal_datetime):
        goal = Goal(goal_type=goal_type, 
                    start_datetime=start_datetime, 
                    end_datetime=end_datetime, 
                    campaign=None,
                    name=name,
                    goal_amount=goal_amount,
                    raised_amount=raised_amount)
        goal.save()
        return goal
    else:
        return
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    