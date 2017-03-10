# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime

def add_cp(apps, schema_editor):
    Team = apps.get_model('clubs', 'Team')
    Event = apps.get_model('events', 'Event')
    SessionGroup = apps.get_model('events', 'SessionGroup')
    Session = apps.get_model('events', 'Session')
    StudentClubYear = apps.get_model('core', 'StudentClubYear')
    start_date = datetime.date(2017, 2, 28)
    end_date = datetime.date(2017, 3, 2)
    year_2016_2017 = StudentClubYear.objects.get(start_date__year=2016,
                                                 end_date__year=2017)
    cp_r_team = Team.objects.create(name="فريق تنظيم البرنامج الثقافي - الرياض",
                                    code_name="cp5-r", year=year_2016_2017,
                                    city="الرياض", gender="")
    cp_j_team = Team.objects.create(name="فريق تنظيم البرنامج الثقافي - جدة",
                                    code_name="cp5-r", year=year_2016_2017,
                                    city="جدة", gender="")
    cp_a_team = Team.objects.create(name="فريق تنظيم البرنامج الثقافي - الأحساء",
                                    code_name="cp5-r", year=year_2016_2017,
                                    city="الأحساء", gender="")
    cp_r_event = Event.objects.create(official_name="البرنامج الثقافي",
                                      english_name="Culutre Program - Riyadh",
                                      code_name="cp5-r",
                                      start_date=start_date,
                                      end_date=end_date,
                                      organizing_team=cp_r_team)
    cp_j_event = Event.objects.create(official_name="البرنامج الثقافي",
                                      english_name="Culutre Program - Jeddah",
                                      code_name="cp5-j",
                                      start_date=start_date,
                                      end_date=end_date,
                                      organizing_team=cp_j_team)
    cp_a_event = Event.objects.create(official_name="البرنامج الثقافي",
                                      english_name="Culutre Program - Alahsa",
                                      code_name="cp5-a",
                                      start_date=start_date,
                                      end_date=end_date,
                                      organizing_team=cp_a_team)
    cp_r_session_group_lectures = SessionGroup.objects.create(event=cp_r_event,
                                                              title="محاضرات البرنامج الثقافي الخامس",
                                                              code_name="lectures")
    cp_r_session_group_workshops = SessionGroup.objects.create(event=cp_r_event,
                                                               is_limited_to_one=True,
                                                               title="ورش عمل البرنامج الثقافي الخامس",
                                                               code_name="workshops")
    lecture_names = {datetime.date(2017,2,28): ["أصبوحة شعرية", "الاختلاف مع النسق"],
                     datetime.date(2017,3,1): ["كيف تخرج من الصدفة", "التفكير الإبداعي", "سر الإبداع"]}
    for date in lecture_names:
        for name in lecture_names[date]:
            session = Session.objects.create(name=name,
                                             acceptance_method="F",
                                             date=date,
                                             event=cp_r_event)
            cp_r_session_group_lectures.sessions.add(session)
    workshop_names = {datetime.date(2017,2,28): ["سكامبر، طرق ووسائل الإبداع", "تمارين وتطبيقات لتنمية الإبداع"],
                      datetime.date(2017,3,1): ["تجسيد أفكار منتجات باستخدام الليقو", "صناعة الفكرة الإبداعية"]}
    for date in workshop_names:
        for name in workshop_names[date]:
            session = Session.objects.create(name=name,
                                             acceptance_method="F",
                                             limit=50,
                                             date=date,
                                             event=cp_r_event)
            cp_r_session_group_workshops.sessions.add(session)

def remove_cp(apps, schema_editor):
    Team = apps.get_model('clubs', 'Team')
    Session = apps.get_model('events', 'Session')
    SessionGroup = apps.get_model('events', 'SessionGroup')
    Event = apps.get_model('events', 'Event')
    code_names = ["cp5-r", "cp5-j","cp5-a"]
    Team.objects.filter(code_name__in=code_names).delete()
    Session.objects.filter(event__code_name__in=code_names).delete()
    SessionGroup.objects.filter(event__code_name__in=code_names).delete()
    Event.objects.filter(code_name__in=code_names).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('events', '0029_sessiongroup'),
    ]

    operations = [
        migrations.RunPython(
            add_cp,
            reverse_code=remove_cp),
    ]