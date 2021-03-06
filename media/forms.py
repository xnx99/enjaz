# -*- coding: utf-8  -*-
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm
from django.forms.models import inlineformset_factory

from clubs.models import Club
from clubs.utils import get_media_center

from media.models import EmployeeReport, FollowUpReport, Story, StoryReview, Article, ArticleReview, CustomTask, \
    TaskComment, Poll, \
    PollResponse, WHAT_IF, HUNDRED_SAYS, PollComment, PollChoice, FollowUpReportImage, FollowUpReportAdImage, \
    ReportComment, Buzz, SnapchatReservation


# A nice trick to display full names instead of usernames
# Check: http://stackoverflow.com/questions/16369403/foreign-key-and-select-field-value-in-admin-interface
class CustomUserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        try:
            return obj.common_profile.get_ar_full_name()
        except ObjectDoesNotExist:
            return obj


class EmployeeReportForm(ModelForm):
    class Meta:
        model = EmployeeReport
        fields = ['speaker', 'quotation', 'sponsor_speech',
                  'prize_winner', 'winner_college_or_club', 'booth',
                  'sponsor', 'attendant_count', 'organizer_count',
                  'speaker_count', 'lecture_count', 'session_count',
                  'booth_count', 'end', 'notes']


class FollowUpReportForm(ModelForm):
    class Meta:
        model = FollowUpReport
        fields = ['description', 'twitter_announcement', 'is_draft']


FollowUpReportImageFormset = inlineformset_factory(FollowUpReport, FollowUpReportImage, fields=['image'])
FollowUpReportAdImageFormset = inlineformset_factory(FollowUpReport, FollowUpReportAdImage, fields=['image'])


class ReportCommentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ReportCommentForm, self).__init__(*args, **kwargs)
        self.fields['body'].widget.attrs = {'class': 'form-control autogrow', 'placeholder': u"أضف تعليقًا..."}

    class Meta:
        model = ReportComment
        fields = ['body']


class StoryForm(ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control input-lg', 'placeholder': u'العنوان'}))
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '18', 'placeholder': u'النص'}))

    class Meta:
        model = Story
        fields = ['title', 'text']


class StoryReviewForm(ModelForm):
    notes = forms.CharField(required=False, widget=forms.Textarea(
        attrs={'class': 'form-control', 'rows': '5', 'placeholder': u'الملاحظات'}))
    approve = forms.BooleanField(label=u"اعتمد الخبر.", required=False)

    class Meta:
        model = StoryReview
        fields = ['notes', 'approve']


class ArticleForm(ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control input-lg', 'placeholder': u'العنوان'}))
    text = forms.CharField(required=False,
                           widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '18', 'placeholder': u'النص'}))

    def clean(self):
        cleaned_data = super(ArticleForm, self).clean()
        text = cleaned_data.get("text")
        attachment = cleaned_data.get("attachment")

        if not (text or attachment):
            # If both text and attachment are empty, raise an error
            msg = u"يرجى كتابة نص أو رفع ملف مرفق."
            raise forms.ValidationError(msg)
        elif text and attachment:
            # On the other hand, if both are full raise an error
            msg = u"يرجى كتابة نص أو رفع ملف مرفق. لا يمكن القيام بالاثنين معًَا."
            raise forms.ValidationError(msg)

        return cleaned_data

    class Meta:
        model = Article
        fields = ['title', 'text', 'author_photo', 'attachment']


class ArticleReviewForm(ModelForm):
    notes = forms.CharField(required=False, widget=forms.Textarea(
        attrs={'class': 'form-control', 'rows': '5', 'placeholder': u'الملاحظات'}))
    approve = forms.BooleanField(label=u"اعتمد المقال.", required=False)

    class Meta:
        model = ArticleReview
        fields = ['notes', 'approve']


class TaskForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs = {'class': 'autogrow'}

    # assignee = CustomUserChoiceField(queryset=User.objects.filter(memberships=get_media_center()))

    class Meta:
        model = CustomTask
        fields = ['assignee', 'title', 'description', 'due_date']


class TaskCommentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(TaskCommentForm, self).__init__(*args, **kwargs)
        self.fields['body'].widget.attrs = {'class': 'form-control autogrow', 'placeholder': u"أضف تعليقًا..."}

    class Meta:
        model = TaskComment
        fields = ['body']


class PollForm(ModelForm):
    poll_type = forms.HiddenInput()

    class Meta:
        model = Poll
        exclude = ('poll_type', 'date_created', 'creator')


PollChoiceFormSet = inlineformset_factory(Poll, PollChoice, fields=['value'])


class PollResponseForm(ModelForm):
    """
    A form that handles responses to a poll with choices (hundred-says)
    """

    def __init__(self, *args, **kwargs):
        # Make sure an instance is passed and it has a poll specified
        assert 'instance' in kwargs
        assert getattr(kwargs['instance'], 'poll') is not None
        super(PollResponseForm, self).__init__(*args, **kwargs)
        # Limit the available choices to the attached poll's choices
        self.fields['choice'] = forms.ModelChoiceField(queryset=self.instance.poll.choices.all(),
                                                       widget=forms.RadioSelect(),
                                                       label="",
                                                       empty_label=None)  # Remove Django's default "--------" option

    class Meta:
        model = PollResponse
        exclude = ('poll', 'user', 'date')


class PollCommentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PollCommentForm, self).__init__(*args, **kwargs)
        self.fields['body'].widget.attrs = {'class': 'form-control autogrow', 'placeholder': u"أضف تعليقًا..."}

    class Meta:
        model = PollComment
        fields = ('body',)


class PollSuggestForm(forms.Form):
    def __init__(self, poll_type, *args, **kwargs):
        super(PollSuggestForm, self).__init__(*args, **kwargs)
        if poll_type == HUNDRED_SAYS:
            self.fields['choices'] = forms.CharField(label=u"الخيارات", widget=forms.Textarea(), required=False)

    title = forms.CharField(label=u"العنوان", required=False)
    text = forms.CharField(widget=forms.Textarea(), label=u"النص")


class BuzzForm(ModelForm):
    class Meta:
        model = Buzz
        fields = ['title', 'body', 'image', 'colleges',
                  'announcement_date', 'is_push']


class SnapchatReservationForm(ModelForm):
    start_time = forms.TimeField(
        input_formats=("%I:%M %p", "%H:%M:%S", "%H:%M"),
        label=u"وقت البداية",
    )
    end_time = forms.TimeField(
        input_formats=("%I:%M %p", "%H:%M:%S", "%H:%M"),
        label=u"وقت النهاية",
    )

    class Meta:
        model = SnapchatReservation
        fields = ['club', 'date', 'start_time', 'end_time']
