# coding=utf-8
import ckeditor.fields
from django.db import models
from django.utils.translation import ugettext_lazy as _


class AbstractRequest(models.Model):
    submission_datetime = models.DateTimeField(
        _(u"وقت تقديم الطلب"),
        auto_now_add=True,
    )

    class Meta:
        abstract = True


class ActivityRequest(AbstractRequest):
    # When the activity creation request is first created, this field should initially be blank. Once
    # the request is approved, an `Activity` object is created and linked to the request via this
    # field. For activity update requests, it should be set to the activity that is going to be
    # updated.
    activity = models.ForeignKey(
        _(u"النشاط"),
        to='activities2.Activity',
        null=True, blank=True,
    )

    name = models.CharField(_(u"اسم النشاط"), max_length=200)
    description = ckeditor.fields.RichTextField(_(u"وصف النشاط"))

    # This is a flag to distinguish update from creation requests
    is_update_request = models.BooleanField(
        _(u"نوع الطلب"),
        choices=(
            (False, _(u"طلب إضافة")),
            (True, _(u"طلب تعديل")),
        ),
        default=False,
    )

    class Meta:
        verbose_name = _(u"طلب نشاط")
        verbose_name_plural = _(u"طلبات أنشطة")


class ActivityCancelRequest(AbstractRequest):
    activity = models.ForeignKey(
        _(u"النشاط"),
        to='activities2.Activity',
    )

    class Meta:
        verbose_name = _(u"طلب إلغاء نشاط")
        verbose_name_plural = _(u"طلبات إلغاء أنشطة")


class AbstractRequestAttachment(models.Model):
    activity_request = models.ForeignKey(
        _(u"طلب النشاط"),
        to='approvals.ActivityRequest',
        related_name='%(class)ss'
    )

    class Meta:
        abstract = True


class DescriptionField(AbstractRequestAttachment):
    label = models.CharField(_(u"الوصف"), max_length=50)
    value = models.CharField(_(u"القيمة"), max_length=200)

    class Meta:
        verbose_name = _(u"حقل وصفي")
        verbose_name_plural = _(u"حقول وصفية")


class EventSubRequest(AbstractRequestAttachment):
    label = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=50)

    class Meta:
        verbose_name = _(u"طلب فعالية")
        verbose_name_plural = _(u"طلبات فعاليات")


class RequestThread(object):
    pass
