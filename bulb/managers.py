from django.db import models
from django.utils import timezone
from core.models import StudentClubYear
from accounts.utils import get_user_city, get_user_gender

class BookQuerySet(models.QuerySet):
    def current_year(self):
        year = StudentClubYear.objects.get_current()
        return self.filter(year=year)

    def available(self):
        """
        Return a queryset of approved books.
        """
        return self.filter(is_available=True, is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)

    def of_user(self, user):
        return self.filter(submitter=user)
    
    def for_user_gender(self, user=None):
        gender_condition = models.Q()

        if user and user.is_authenticated():
            gender = get_user_gender(user)
            if gender:
                gender_condition = models.Q(submitter__common_profile__college__gender=gender)
        return self.filter(gender_condition)

    def for_user_city(self, user=None):
        city_condition = models.Q()

        if user and user.is_authenticated():
            city = get_user_city(user)
            if city:
                city_condition = models.Q(submitter__common_profile__city=city)
        return self.filter(city_condition)

class RequestQuerySet(models.QuerySet):
    def current_year(self):
        year = StudentClubYear.objects.get_current()
        return self.filter(book_year=year)

    def to_user(self, user):
        return self.filter(book__submitter=user)

    def by_user(self, user):
        return self.filter(requester=user)

    def pending(self):
        return self.filter(requester_status='', owner_status='')

    def canceled(self):
        return self.filter(is_canceled=True)

    def successful(self):
        return self.filter(requester_status='D') | \
               self.filter(owner_status='D')

    def disputed(self):
        return (
            self.filter(requester_status='D',
                        owner_status='F') |\
            self.filter(requester_status='F',
                        owner_status='D')
        ).exclude(is_canceled=True)

class PointQuerySet(models.QuerySet):
    def current_year(self):
        year = StudentClubYear.objects.get_current()
        return self.filter(year=year)

    def counted(self):
        return self.filter(is_counted=True)

    def count_total(self):
        total = self.current_year().counted().aggregate(total_points=models.Sum('value'))['total_points']
        if total is None:
            return 0
        else:
            return total 
