# -*- coding: utf-8  -*-
"""
Tests for the activities app.
"""
from datetime import datetime, date, time

from django.test import TestCase

from django.contrib.auth import login
from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse

from clubs.models import Club
from activities.models import Activity, Episode

def create_club():
    return Club.objects.create(name="Test Club Arabic Name",
                               english_name="Test English Club Name",
                               description="-",
                               email="test@enjazportal.com",
                               )

def create_activity(club=Club.objects.get(pk=1),
                    submitter=User.objects.get(pk=1),
                    collect_participants=False,
                    episode_count=1,
                    ):
    activity =  Activity.objects.create(primary_club=club,
                                       name='Test Activity',
                                       description='Test Description',
                                       participants=1,
                                       organizers=1,
                                       submitter=submitter,
                                       collect_participants=collect_participants,
                                       )
    for i in range(episode_count):
        Episode.objects.create(activity=activity,
                               start_date=date.today(),
                               end_date=date.today(),
                               start_time=datetime.now(),
                               end_time=datetime.now(),
                               location='Test Location',
                               )
    return activity

def create_user(username):
    return User.objects.create_user(username, 'test@enjazportal.com', '12345678')

class ShowActivityViewTests(TestCase):
    def test_show_view_with_a_normal_user(self):
        """
        Test the show activity view with a user with no permissions.
        """
        # Setup the database
        normal_user = create_user('normal_user')
        club = create_club()
        activity = create_activity(submitter=normal_user)
        
        # Login
        logged_in = self.client.login(username=normal_user.username, password='12345678')
        self.assertEqual(logged_in, True)
        
        # Go to the view
        response = self.client.get(reverse('activities:show',
                                           args=(activity.pk, )))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, activity.name)
        self.assertContains(response, activity.primary_club.name)
        self.assertContains(response, activity.description)
        # Normal user should not see activity status
        self.assertNotContains(response, 'tooltip-primary')
        # Normal user should not see edit button
        self.assertNotContains(response, 'href="' + reverse('activities:edit',
                                                            args=(activity.pk, )) + '"'
                               )
        # Normal user should not see review buttons
        self.assertNotContains(response, u'مراجعة رئاسة نادي الطلاب')
        self.assertNotContains(response, u'مراجعة عمادة شؤون الطلاب')
        
    def test_show_view_with_a_normal_user_and_collect_participants(self):
        """
        Test whether the user can see participate button.
        """
        # Setup the database
        normal_user = create_user('normal_user')
        club = create_club()
        activity = create_activity(submitter=normal_user,
                                   collect_participants=True)
        
        # Login
        logged_in = self.client.login(username=normal_user.username, password='12345678')
        self.assertEqual(logged_in, True)
        
        response = self.client.get(reverse('activities:show',
                                   args=(activity.pk, )))
        self.assertContains(response, 'href="' + reverse('activities:participate',
                                                         args=(activity.pk, )) + '"'
                            )
        
    def test_show_view_with_a_privileged_user(self):
        privileged_user = create_user('user2')
        
        view_activity = Permission.objects.get(codename='view_activity')
        change_activity = Permission.objects.get(codename='change_activity')
        view_deanship_review = Permission.objects.get(codename='view_deanship_review')
        view_presidency_review = Permission.objects.get(codename='view_presidency_review') 
        privileged_user.user_permissions.add(view_activity, change_activity,
                                             view_deanship_review, view_presidency_review)
        
        club = create_club()
        activity = create_activity(submitter=privileged_user)
        
        # Login
        logged_in = self.client.login(username=privileged_user.username, password='12345678')
        self.assertEqual(logged_in, True)
        
        # Go to the view
        response = self.client.get(reverse('activities:show',
                                           args=(activity.pk, )))
        
        # Housekeeping tests
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, activity.name)
        self.assertContains(response, activity.primary_club.name)
        self.assertContains(response, activity.description)
        
        # Privileged user should see activity status
        self.assertContains(response, 'tooltip-primary')
        # Privileged user should see edit button
        self.assertContains(response, 'href="' + reverse('activities:edit',
                                                        args=(activity.pk, )) + '"'
                            )
        # Privileged user should see review buttons
        self.assertContains(response, u'مراجعة رئاسة نادي الطلاب')
        self.assertContains(response, u'مراجعة عمادة شؤون الطلاب')
        
class ReviewViewTests(TestCase):
    def test_review_view_with_normal_user(self):
        # Setup the database
        normal_user = create_user('normal_user')
        club = create_club()
        activity = create_activity(submitter=normal_user)
        
        # Login
        logged_in = self.client.login(username=normal_user.username, password='12345678')
        self.assertEqual(logged_in, True)
        
        # Go to the view
        response = self.client.get(reverse('activities:review',
                                           args=(activity.pk, )))
        self.assertEqual(response.status_code, 403) # Forbidden
