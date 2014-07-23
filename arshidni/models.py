# -*- coding: utf-8  -*-
import math

from django.db import models
from django.contrib.auth.models import User

from clubs.models import College, college_choices


is_published_choices = (
    (None, u'لم يراجع بعد'),
    (True, u'منشور'),
    (False, u'محذوف'),
)

is_accepted_choices = (
    (None, u'لم تراجع بعد'),
    (True, u'مقبول'),
    (False, u'مرفوض'),
)

group_status_choices = (
    ('P', u'تنتظر المراجعة'),
    ('A', u'مقبولة'),
    ('R', u'مرفوضة'),
)

class ArshidniProfile(models.Model):
    interests = models.TextField(u"الاهتمامات", help_text=u"ما هي اهتمامتك الأكاديمية؟")
    contacts = models.CharField(max_length=100,
                                verbose_name=u"طريقة التواصل", help_text=u"جوال مثلا؟")
    is_published = models.NullBooleanField(verbose_name=u"منشور؟",
                                           default=True,
                                           choices=is_published_choices)
    submission_date = models.DateTimeField(u'تاريخ الإرسال',
                                           auto_now_add=True)
    edit_date = models.DateTimeField(u'تاريخ التعديل', auto_now=True)

# Graduates

class GraduateProfile(ArshidniProfile):
    user = models.OneToOneField(User, null=True,
                                on_delete=models.SET_NULL,
                                verbose_name=u"المستخدم",
                                related_name="graduate_profile")
    bio = models.TextField(u"نبذة", help_text=u"متى تخرجت؟ هل خضت أي اختبارات عالمية؟ هل التحقت بأي برامج؟")
    answers_questions = models.BooleanField(verbose_name=u"هل تريد الإجابة على أسئلة الطلاب؟",
                                            default=True)
    gives_lectures = models.BooleanField(verbose_name=u"هل تريد إلقاء محاضرات للطلاب عن موضوع من اختيارك؟",
                                            default=True)

class Question(models.Model):
    submitter = models.ForeignKey(User, null=True,
                                  on_delete=models.SET_NULL,
                                  verbose_name=u"المرسل")
    text = models.TextField(u"نص السؤال")
    # We don't use a ForeignKey with College because that one is
    # multiplied by the sections.  We don't want that.
    college = models.CharField(max_length=1, choices=college_choices,
                               verbose_name=u"الكلية")
    is_published = models.NullBooleanField(verbose_name=u"منشور؟",
                                           default=True,
                                           choices=is_published_choices)
    is_answered = models.BooleanField(verbose_name=u"هل أجيب عنه؟",
                                      default=False)
    is_editable = models.BooleanField(verbose_name=u"يمكن تعديله؟",
                                      default=True)
    submission_date = models.DateTimeField(u'تاريخ الإرسال',
                                           auto_now_add=True)
    edit_date = models.DateTimeField(u'تاريخ التعديل', auto_now=True)

    def get_title(self):
        "Return the first 40 character of text field."
        if len(self.text) > 40:
            return self.text[:40] + u"..."
        else:
            return self.text

    def get_college_name(self):
        college_dict = dict(college_choices)
        upper_college = self.college.upper()
        return college_dict[upper_college]

    def is_edited(self):
        """If the difference between submission_date and edit_date is
        more than 10 minutes.  Consider it edited. """
        delta_time = edit_date - submission_date
        if delta_time.seconds >= 600:
            return True
        else:
            return False

    class Meta:
        verbose_name = u"سؤال أكاديمي"
        verbose_name_plural = u"الأسئلة الأكاديمية"


class Answer(models.Model):
    submitter = models.ForeignKey(User, null=True,
                                  on_delete=models.SET_NULL,
                                  verbose_name=u"المرسل")
    question = models.ForeignKey(Question, null=True,
                                 on_delete=models.SET_NULL,
                                 verbose_name=u"المرسل")
    # parent is only meant for future implementation to allow threads.
    parent = models.ForeignKey('self', null=True, default=None,
                               blank=True,
                               on_delete=models.SET_NULL,
                               verbose_name=u"التعليق الأب")
    text = models.TextField(u"النص")
    is_published = models.NullBooleanField(verbose_name=u"منشور؟",
                                           default=True,
                                           choices=is_published_choices)
    is_editable = models.BooleanField(verbose_name=u"يمكن تعديله؟",
                                      default=True)
    submission_date = models.DateTimeField(u'تاريخ الإرسال',
                                           auto_now_add=True)
    edit_date = models.DateTimeField(u'تاريخ التعديل', auto_now=True)

# Groups

class StudyGroup(models.Model):
    coordinator = models.ForeignKey(User, null=True,
                                    on_delete=models.SET_NULL,
                                    related_name="studygroup_coordination",
                                    verbose_name=u"المنسق")
    name = models.CharField(max_length=100, verbose_name=u"الاسم")
    starting_date = models.DateField(u'تاريخ البدء')
    ending_date = models.DateField(u'تاريخ الانتهاء')
    max_members = models.PositiveSmallIntegerField(verbose_name=u"العدد الأقصى للأعضاء",
                                                   help_text=u"يجب أن يكون بين 3 و 8.")
    members = models.ManyToManyField(User, null=True,
                                     verbose_name=u"الأعضاء",
                                     blank=True,
                                     related_name="studygroup_memberships")
    is_published = models.NullBooleanField(verbose_name=u"منشور؟",
                                           default=True,
                                           choices=is_published_choices)
    status = models.CharField(max_length=1, verbose_name=u"الحالة",
                              default='P', choices=group_status_choices)
    
    submission_date = models.DateTimeField(u'تاريخ الإرسال',
                                           auto_now_add=True)
    edit_date = models.DateTimeField(u'تاريخ التعديل', auto_now=True)

    def get_period_in_days(self):
        return (self.ending_date - self.starting_date).days

    get_period_in_days.short_description = u"المدة بالأيام"

    def get_period_in_weeks(self):
        float_weeks = (self.ending_date - self.starting_date).days / 7.0
        # Round up
        weeks = math.ceil(float_weeks)
        return int(weeks)

    get_period_in_weeks.short_description = u"المدة بالأسابيع"

    def get_remaining_members(self):
        current_members = self.members.count()
        return self.max_members - current_members

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u"مجموعة دراسية"
        verbose_name_plural = u"المجموعات الدراسية"


class LearningObjective(models.Model):
    group = models.ForeignKey(StudyGroup, null=True,
                              on_delete=models.SET_NULL,
                              verbose_name=u"المجموعة")
    text = models.CharField(max_length=100, verbose_name=u"الوصف")
    is_done = models.BooleanField(verbose_name=u"هل أنجز؟",
                                      default=False)
    submission_date = models.DateTimeField(u'تاريخ الإرسال',
                                           auto_now_add=True)

class JoinStudyGroupRequest(models.Model):
    # TODO: Add status
    submitter = models.ForeignKey(User, null=True,
                                  on_delete=models.SET_NULL,
                                  verbose_name=u"المرسل")
    group = models.ForeignKey(StudyGroup, null=True,
                              on_delete=models.SET_NULL,
                              verbose_name=u"المجموعة",
                              related_name="join_requests")
    is_accepted = models.NullBooleanField(verbose_name=u"مقبول؟",
                                           default=None,
                                           choices=is_accepted_choices)
    submission_date = models.DateTimeField(u'تاريخ الإرسال',
                                           auto_now_add=True)

    def get_full_status(self):
        is_accepted_dict = dict(is_accepted_choices)
        return is_accepted_dict[self.is_accepted]

# Studnet Colleague

class ColleagueProfile(ArshidniProfile):
    user = models.OneToOneField(User, null=True,
                                on_delete=models.SET_NULL,
                                verbose_name=u"المستخدم",
                                related_name="colleague_profile")
    bio = models.TextField(u"نبذة", help_text=u"هل خضت أي اختبارات عالمية؟ هل تدربت في مستشفى؟ هل شاركت في أبحاث؟")
    batch = models.PositiveSmallIntegerField(verbose_name=u"الدفعة")
    # The following field can be dynamically predicted but this can be
    # very expensive.
    is_available = models.BooleanField(verbose_name=u"هل هو متاح؟",
                                            default=True)
    
class SupervisionRequest(models.Model):    
    user = models.ForeignKey(User, null=True,
                             on_delete=models.SET_NULL,
                             verbose_name=u"المستخدم",
                             related_name="supervision_requests")
    colleague = models.ForeignKey(ColleagueProfile, null=True,
                                  on_delete=models.SET_NULL,
                                  verbose_name=u"المستخدم",
                                  related_name="colleague")
    status_choices = (
        ('P', u'تنتظر المراجعة'),
        ('A', u'مقبول'), # Currently accepted
        ('R', u'مرفوض'), # Never been accepted
        ('D', u'ألغاه الطالب المستجد قبل أن يراجعه الزميل الطلابي'), # Never been accepted
        ('WN', u'ألغاه الطالب المستجد'), # After it has been accepted
        ('WC', u'ألغاه الزميل الطلابي'), # After it has been accepted
    )
    status = models.CharField(max_length=2, verbose_name=u"الحالة",
                              default='P',
                              choices=status_choices)
    contacts = models.CharField(max_length=100,
                                verbose_name=u"طريقة التواصل", help_text=u"جوال مثلا؟")
    interests = models.TextField(u"الاهتمامات", help_text=u"ما المجالات التي تريد تطوير نفسك فيها؟")
    batch = models.PositiveSmallIntegerField(verbose_name=u"الدفعة")
    submission_date = models.DateTimeField(u'تاريخ الإرسال',
                                           auto_now_add=True)
    withdrawal_date = models.DateTimeField(u'تاريخ السحب',
                                           null=True,
                                           default=None)
    edit_date = models.DateTimeField(u'تاريخ التعديل', auto_now=True)

    def get_full_status(self):
        status_dict = dict(self.status_choices)
        return status_dict[self.status]
