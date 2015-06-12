# -*- coding: utf-8  -*-
from django.contrib import admin
from clubs.models import Club, College, city_choices, gender_choices
from accounts.admin import deanship_admin

class ClubFilter(admin.SimpleListFilter):
    title = u"نوع النادي"
    parameter_name = 'type'
    def lookups(self, request, model_admin):
        return (
            ('p', u'الرئاسة'),
            ('s', u'نادي فرعي'),
            ('c', u'نادي كلية'),
            )

    def queryset(self, request, queryset):
        if self.value() == 'p':
            return queryset.filter(english_name='Presidency')
        elif self.value() == 'c':
            return queryset.exclude(college__isnull=True)
        elif self.value() == 's':
            return queryset.filter(college__isnull=True).exclude(pk=1)

class CityFilter(admin.SimpleListFilter):
    title = u"المدينة"
    parameter_name = 'city'
    def lookups(self, request, model_admin):
        return city_choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(city=self.value())

class GenderFilter(admin.SimpleListFilter):
    title = u"الجنس"
    parameter_name = 'gender'
    def lookups(self, request, model_admin):
        return gender_choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(gender=self.value())
        
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'english_name', 'email', 'coordinator', 'number_of_members')
    list_filter = (ClubFilter, CityFilter, GenderFilter)
    filter_horizontal = ('members', 'deputies')

    def number_of_members(self, obj):
        return obj.members.count()
    number_of_members.short_description = u"عدد الأعضاء"

class CollegeAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'section', 'gender')
    list_filter = (CityFilter, GenderFilter)

admin.site.register(College, CollegeAdmin)
admin.site.register(Club, ClubAdmin)
deanship_admin.register(Club, ClubAdmin)
