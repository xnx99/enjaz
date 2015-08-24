"""Utility functions related to the clubs app."""
from .models import Club
from core.models import StudentClubYear


current_year = StudentClubYear.objects.get_current()

def is_coordinator_of_any_club(user):
    """Return whether the user is a coordinator of any club."""
    return user.coordination.current_year().exists()

def is_deputy_of_any_club(user):
    """Return whether the user is a deputy of any club."""
    return Club.objects.current_year().filter(deputies=user).exists()

def is_member_of_any_club(user):
    """Return whether the user is a member of any club."""
    user_clubs = Club.objects.current_year().filter(members=user)
    return user_clubs.exists()

def is_employee_of_any_club(user):
    """Return whether the user is an employee of any club."""
    employee_clubs = Club.objects.current_year().filter(employee=user)
    return employee_clubs.exists()

def is_coordinator(club, user):
    """Return whether the user is the coordinator of a given club."""
    return club.coordinator == user

def is_deputy(club, user):
    """Return whether the user is a member of a given club."""
    return user in club.deputies.filter(pk=user.pk)

def is_member(club, user):
    """Return whether the user is a member of a given club."""
    return user in club.members.filter(pk=user.pk)

def is_coordinator_or_member(club, user):
    """Return whether the user is the coordinator, a deputy or a member of a given club."""
    return is_coordinator(club, user) or is_deputy(club, user) or is_member(club, user)

def is_coordinator_or_deputy(club, user):
    """Return whether the user is the coordinator or a deputy of a given club."""
    return is_coordinator(club, user) or is_deputy(club, user)

def is_employee(club, user):
    """Return whether the user is the employee assigned to a given club."""
    return user == club.employee

def has_coordination_to_activity(user, activity):
    """Return whether the user is the coordinator or deputy assigned to
    any of the primry or secondary clubs of a given activity.
    """
    # First get clubs associated with the activity.  We need both of
    # them to be QuerySets
    activity_primary_club = Club.objects.filter(
                            id=activity.primary_club.id)
    activity_secondary_clubs = activity.secondary_clubs.all()
    activity_clubs = activity_primary_club | activity_secondary_clubs
    # Second, check if any of which have the given user as a
    # coordinator or deputy
    coordination_clubs = activity_clubs.filter(coordinator=user) | \
                         activity_clubs.filter(deputies=user)
    # Return a Boolean 
    return coordination_clubs.exists()

def get_deanship():
    return Club.objects.get(english_name="Deanship of Student Affairs",
                            year=current_year)

def get_presidency():
    return Club.objects.get(english_name="Presidency",
                            year=current_year)

def get_media_center():
    return Club.objects.get(english_name="Media Center",
                            year=current_year, city='R',
                            gender='M')

def get_user_clubs(user):
    return user.memberships.current_year() | user.coordination.current_year()

def get_user_coordination_and_deputyships(user):
    """Return the clubs in which the given user is the coordinator or
    deputy.  Returns None if no clubs are found."""

    coordination = user.coordination.current_year()
    deputyships = user.deputyships.current_year()
    # Return a QuerySet to allow further filtering
    return (coordination | deputyships)

def is_coordinator_or_deputy_of_any_club(user):
    """Return whether the user is a coordinator of any club."""
    coordination_and_deputyships = get_user_coordination_and_deputyships(user)
    return coordination_and_deputyships.exists()

def forms_editor_check(user, object):
    """A function to evaluate if user is eligible to create/edit forms for clubs."""
    # Confirm that the passed object is a ``Club`` instance
    if not isinstance(object, Club):
        raise TypeError("Expected a Club object, received %s" % type(object))
    return is_coordinator_or_deputy(object, user) or user.is_superuser

def can_review_activity(user, activity):
    if user.has_perm('activities.add_review'): # e.g. superuser
        return True
    reviewing_parents = Club.objects.activity_reviewing_parents(activity)
    user_clubs = reviewing_parents.filter(coordinator=user) | \
                 reviewing_parents.filter(deputies=user)
    return user_clubs.exists()

def can_delete_activity(user, activity):
    # A user can delete an activity in three cases:
    # * If they have the change_activity permission (e.g. superuser).
    # * If they are the submitter, coordinator or deputy and the
    #   activity is not reviewed yet.
    # * If they are the coordinator or deputy of any club that can
    #   review the activity, if that club has can_delete=True.  In
    #   real life, this means vice presidents.
    if user.has_perm('activities.change_activity'):
        return True
    elif activity.is_editable and \
       not activity.review_set.exists() and \
       (activity.submitter == user or \
       has_coordination_to_activity(user, activity)):
        return True
    else:
        reviewing_parents = Club.objects.activity_reviewing_parents(activity)
        deleting_parents = reviewing_parents.filter(can_delete=True)
        user_clubs = deleting_parents.filter(coordinator=user) | deleting_parents.filter(deputies=user)
        return user_clubs.exists()

def can_edit_activity(user, activity):
    # A user can edit an activity in three cases:
    # * If they have the change_activity permission (e.g. superuser).
    # * If they are the submitter, coordinator or deputy and the
    #   activity is_editable=True.
    # * If they are the coordinator or deputy of any club that can
    #   review the activity, if that club has can_edit=True.  In
    #   real life, this means vice presidents.
    if user.has_perm('activities.change_activity'):
        return True
    elif activity.is_approved == False and \
         (activity.submitter == user or \
         has_coordination_to_activity(user, activity)):
        return False
    elif (activity.submitter == user or \
          has_coordination_to_activity(user, activity)):
        # This doesn't necessarily mean that they would be able to
        # edit the activity fully.  Further restriction is to be
        # imposed in the view.
        return True
    else:
        reviewing_parents = Club.objects.activity_reviewing_parents(activity)
        editing_parents = reviewing_parents.filter(can_edit=True)
        user_clubs = editing_parents.filter(coordinator=user) | editing_parents.filter(deputies=user)
        return user_clubs.exists()

def can_review_any_niqati(user):
    if user.has_perm('activities.change_code'): # e.g. superuser
        return True
    niqati_reviewers = Club.objects.filter(can_review_niqati=True)
    user_clubs = niqati_reviewers.filter(coordinator=user) | \
                 niqati_reviewers.filter(deputies=user)
    return user_clubs.exists()

def get_order_reviewing_clubs_by_user(user, order):
    niqati_reviewers = Club.objects.niqati_reviewing_parents(order)
    user_clubs = niqati_reviewers.filter(coordinator=user) | \
                 niqati_reviewers.filter(deputies=user)
    return user_clubs

def get_club_assessing_clubs_by_user(user, club):
    # Three user types can assess a given activity:
    # * Superuser (which we are not handling here)
    # * Clubs with can_assess (i.e. Student Club president deputies)
    # * Medica Club in the same city
    user_clubs =  user.coordination.current_year() | user.deputyships.current_year()

    # In Riyadh, there are two Media Centers for each gender.
    if club.city == 'R' and club.gender:
        media_center_gender = club.gender
    elif club.city == 'R' and not club.gender:
        # Just in case a Riyadh club doesn't have a gender
        # (i.e. presidency), fall back to male Media Center.
        media_center_gender = 'M'
    else: # For other cities
        media_center_gender = ''
    
    user_media_center = user_clubs.filter(english_name__contains='Media Center',
                                          city=club.city, gender=media_center_gender)

    club_assessing_clubs = Club.objects.club_assessing_parents(club)
    user_assessing_clubs = club_assessing_clubs.filter(coordinator=user) | \
                           club_assessing_clubs.filter(deputies=user)
    return user_assessing_clubs | user_media_center

def can_assess_club(user, club, category=""):
    # Three user types can assess a given activity:
    # * Superuser
    # * Clubs with can_assess (i.e. student club president deputies)
    # * Medica Club in the same city
    if user.has_perms('activities.add_assessment'): # e.g. superuser
        return True
    user_clubs = get_club_assessing_clubs_by_user(user, club)
    return user_clubs.exists()

def can_view_assessments(user, club):
    # Two user types can view assessments a given activity:
    # * Superuser
    # * Clubs with can_view_assessment (i.e. student club president deputies)
    if user.has_perms('activities.delete_assessment'): # e.g. superuser
        return True
    user_clubs = get_club_assessing_clubs_by_user(user, club).filter(can_view_assessments=True)
    return user_clubs.exists()
