# -*- coding: utf-8  -*-
from core.models import Tweet, TwitterAccess
from django.db import models
import operator

BASIC_SEARCH_FIELDS = ['user__pk', 'user__username', 'user__email',
                       'user__common_profile__en_first_name',
                       'user__common_profile__en_middle_name',
                       'user__common_profile__en_last_name',
                       'user__common_profile__ar_first_name',
                       'user__common_profile__ar_middle_name',
                       'user__common_profile__ar_last_name',
                       'user__common_profile__student_id',
                       'user__common_profile__badge_number',
                       'user__common_profile__mobile_number']

def create_tweet(user, text):
    if not user.social_auth.exists():
        return
    else:
        Tweet.objects.create(user=user, text=text)

def create_tweet_by_access(access_code_name, text, media_path=None):
    try:
        access = TwitterAccess.objects.get(code_name=access_code_name)
    except TwitterAccess.DoesNotExist:
        return
    Tweet.objects.create(access=access, text=text, media_path=media_path)

def hindi_to_arabic(number):
    return number.replace(u'٠', '0')\
                 .replace(u'١', '1')\
                 .replace(u'٢', '2')\
                 .replace(u'٣', '3')\
                 .replace(u'٤', '4')\
                 .replace(u'٥', '5')\
                 .replace(u'٦', '6')\
                 .replace(u'٧', '7')\
                 .replace(u'٨', '8')\
                 .replace(u'٩', '9')


def get_search_queryset(queryset, search_fields, search_term):
    # Based on the Django app search functionality found in the
    # function get_search_results of django/contrib/admin/options.py.
    if search_term:
        orm_lookups = [search_field + '__icontains'
                       for search_field in search_fields]
        for bit in search_term.split():
            or_queries = [models.Q(**{orm_lookup: bit})
                          for orm_lookup in orm_lookups]
            queryset = queryset.filter(reduce(operator.or_, or_queries))

    return queryset

