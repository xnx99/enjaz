from django import template
from clubs import utils

register = template.Library()

# NOTE that in filters that take 2 arguments, the arguments of the filter are the opposite of the util function
# (in terms of order)

@register.filter
def is_coordinator_of_any_club(user):
    return utils.is_coordinator_of_any_club(user)

@register.filter
def is_member_of_any_club(user):
    return utils.is_member_of_any_club(user)

@register.filter
def is_employee_of_any_club(user):
    return utils.is_employee_of_any_club(user)

@register.filter
def is_coordinator(user, club):
    return utils.is_coordinator(club, user)

@register.filter
def is_deputy(user, club):
    return utils.is_deputy(club, user)

@register.filter
def is_member(user, club):
    return utils.is_member(club, user)

@register.filter
def is_coordinator_or_member(user, club):
    return utils.is_coordinator_or_member(club, user)

@register.filter
def is_coordinator_or_deputy(user, club):
    return utils.is_coordinator_or_deputy(club, user)

@register.filter
def is_employee(user, club):
    return utils.is_employee(club, user)

@register.filter
def has_coordination_to_activity(user, activity):
    return utils.has_coordination_to_activity(user, activity)