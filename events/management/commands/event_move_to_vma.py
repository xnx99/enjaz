# -*- coding: utf-8  -*-
import os
import urllib2
import unicodecsv

from django.core.management.base import BaseCommand

from events.models import Session, Registration
from events.utils import register_in_vma


class Command(BaseCommand):
    help = "Delete repeated non-user repetitions."

    def add_arguments(self, parser):
        parser.add_argument('--directory', dest='directory',
                            default=None, type=str)
        parser.add_argument('--session', dest='session',
                            default=None, type=int)

    def handle(self, *args, **options):
        directory = options['directory']
        session = options['session']
        if directory:
            csv_files = os.listdir(directory)
            self.stdout.write("Included files are: {}".format(", ".join(csv_files)))
        if session:
            sessions = Session.objects.filter(pk=session)
        else:
            sessions = Session.objects.filter(vma_id__isnull=False)
        for session in sessions:
            if directory:
                csv_filename = str(session.pk) + '.csv'
                full_path = os.path.join(directory, csv_filename)
            if directory and os.path.isfile(full_path):
                self.stdout.write("{} exists".format(full_path))
                csv_file = open(full_path)
                csv_reader = unicodecsv.reader(csv_file, encoding="utf-8")
                for row in csv_reader:
                    email = row[4]
                    registration = (Registration.objects.filter(is_deleted=False, nonuser__email=email) | \
                                    Registration.objects.filter(is_deleted=False, user__email=email)).first()
                    if not registration:
                        self.stdout.write("Registration is None.".format(email))
                        continue
                    elif session in registration.moved_sessions.all():
                        #self.stdout.write("{} was already moved".format(email))
                        continue
                    elif registration.is_deleted:
                        self.stdout.write("{} was deleted".format(email))
                        continue
                    try:
                        register_in_vma(session, registration)
                    except (UnicodeEncodeError, KeyError), e:
                        print e
                        self.stdout.write("Error with registration {}.".format(registration.pk))
            else:
                while True:
                    answer = raw_input(u"Do you want to accept everybody for {}? (Y) ".format(session.pk))
                    if answer.lower() == 'y':
                        break
                registrations = session.get_all_registrations()
                for registration in registrations.filter(is_deleted=False).exclude(moved_sessions=session):
                    try:
                        register_in_vma(session, registration)
                    except (UnicodeEncodeError, KeyError), e:
                        print e
                        self.stdout.write("Error with {}!".format(registration.pk))
