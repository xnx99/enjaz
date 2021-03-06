# -*- coding: utf-8  -*-
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist

from hpc.models import Abstract, Session, Registration, NonUser

class AbstractUniversityFilter(admin.SimpleListFilter):
    title = "University"
    parameter_name = 'university'
    def lookups(self, request, model_admin):
        return (
            ('ksauhs', 'KSAU-HS'),
            ('other', 'Others')
            )

    def queryset(self, request, queryset):
        if self.value() == 'ksauhs':
            return queryset.filter(university='KSAU-HS')
        elif self.value() == 'other':
            return queryset.exclude(university='KSAU-HS')

class EvaluationFilter(admin.SimpleListFilter):
    title = "Evaluation"
    parameter_name = 'evaluation'
    def lookups(self, request, model_admin):
        return (
            ('evaluated', 'Evaluated'),
            ('pending', 'Pending')
            )

    def queryset(self, request, queryset):
        if self.value() == 'evaluated':
            return queryset.filter(evaluation__isnull=False)
        elif self.value() == 'pending':
            return queryset.filter(evaluation__isnull=True)

class RegistrationUniversityFilter(admin.SimpleListFilter):
    title = "University"
    parameter_name = 'university'
    def lookups(self, request, model_admin):
        return (
            ('ksauhs', 'KSAU-HS'),
            ('other', 'Others')
            )

    def queryset(self, request, queryset):
        if self.value() == 'ksauhs':
            return queryset.filter(user__isnull=False)
        elif self.value() == 'other':
            return queryset.filter(nonuser__isnull=False)

class SessionFilter(admin.SimpleListFilter):
    title = "Session"
    parameter_name = 'session'
    def lookups(self, request, model_admin):
        return Session.objects.values_list('pk', 'name') 

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(sessions__pk=self.value())

class AbstractAdmin(admin.ModelAdmin):
    list_display = ['title', 'university', 'college',
                    'presentation_preference', 'date_submitted',
                    'was_evaluated']
    list_filter = ['presentation_preference', 'level',
                   AbstractUniversityFilter, EvaluationFilter]

    def was_evaluated(self, obj):
        try:
            evaluation = obj.evaluation
            return True
        except ObjectDoesNotExist:
            return False
    was_evaluated.boolean = True

class RegistrationAdmin(admin.ModelAdmin):
    list_display = ['pk', '__unicode__', 'get_university', 'get_college',
                    'date_submitted']
    list_filter = [RegistrationUniversityFilter, SessionFilter]
    search_fields= ('user__username', 'user__email',
                    'user__common_profile__en_first_name',
                    'user__common_profile__en_middle_name',
                    'user__common_profile__en_last_name',
                    'user__common_profile__ar_first_name',
                    'user__common_profile__ar_middle_name',
                    'user__common_profile__ar_last_name',
                    'user__common_profile__student_id',
                    'user__common_profile__badge_number',
                    'user__common_profile__mobile_number',
                    'user__common_profile__en_first_name',
                    'user__common_profile__en_middle_name',
                    'user__common_profile__en_last_name',
                    'user__common_profile__ar_first_name',
                    'user__common_profile__ar_middle_name',
                    'user__common_profile__ar_last_name',
                    'nonuser__email',
                    'nonuser__mobile_number',
                    'nonuser__en_first_name',
                    'nonuser__en_middle_name',
                    'nonuser__en_last_name',
                    'nonuser__ar_first_name',
                    'nonuser__ar_middle_name',
                    'nonuser__ar_last_name')

class RegistrationInline(admin.StackedInline):
    model = Registration
    extra = 1
    max_num = 1
    fields = ['sessions']
    
class NonUserAdmin(admin.ModelAdmin):
    list_display = ['pk', '__unicode__', 'university', 'college',
                    'with_deleted_registration', 'date_submitted']
    search_fields= ('email',
                    'en_first_name',
                    'en_middle_name',
                    'en_last_name',
                    'ar_first_name',
                    'ar_middle_name',
                    'ar_last_name')

    def with_deleted_registration(self, obj):
        return obj.hpc2016_registration.is_deleted
    with_deleted_registration.boolean = True

    inlines = [RegistrationInline]

admin.site.register(Abstract, AbstractAdmin)
admin.site.register(Session)
admin.site.register(Registration, RegistrationAdmin)
admin.site.register(NonUser, NonUserAdmin)
