from __future__ import unicode_literals

from django.conf import settings as django_settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext, ugettext_lazy as _
from future.builtins import str

from forms_builder.forms import fields
from forms_builder.forms import settings
from forms_builder.forms.utils import now, slugify, unique_slug
from forms_builder.wrapper import settings as wrapper_settings

STATUS_DRAFT = 1
STATUS_PUBLISHED = 2
STATUS_CHOICES = (
    (STATUS_DRAFT, _("Draft")),
    (STATUS_PUBLISHED, _("Published")),
)


class FormManager(models.Manager):
    """
    Only show published forms for non-staff users.
    """
    def published(self, for_user=None, for_object=None, editor_check=None):
        if for_user is not None and for_object is not None and editor_check is not None\
                and editor_check(for_user, for_object):  # User has permissions to edit forms
            return self.filter(content_type=ContentType.objects.get_for_model(for_object.__class__),
                               object_id=for_object.id)  # Return all forms related to the passed object
        filters = [
            Q(publish_date__lte=now()) | Q(publish_date__isnull=True),
            Q(expiry_date__gte=now()) | Q(expiry_date__isnull=True),
            Q(status=STATUS_PUBLISHED),
            # Q(content_type="", object_id=""), # TODO
        ]
        if settings.USE_SITES:
            filters.append(Q(sites=Site.objects.get_current()))
        return self.filter(*filters)


######################################################################
#                                                                    #
#   Each of the models are implemented as abstract to allow for      #
#   subclassing. Default concrete implementations are then defined   #
#   at the end of this module.                                       #
#                                                                    #
######################################################################

@python_2_unicode_compatible
class AbstractForm(models.Model):
    """
    A user-built form.
    """

    sites = models.ManyToManyField(Site, editable=settings.USE_SITES,
        default=[django_settings.SITE_ID], related_name="%(app_label)s_%(class)s_forms")
    title = models.CharField(_("Title"), max_length=50)
    slug = models.SlugField(_("Slug"), editable=settings.EDITABLE_SLUGS,
        max_length=100, unique=True)
    intro = models.TextField(_("Intro"), blank=True)
    button_text = models.CharField(_("Button text"), max_length=50,
        default=_("Submit"))
    response = models.TextField(_("Response"), blank=True)
    redirect_url = models.CharField(_("Redirect url"), max_length=200,
        null=True, blank=True,
        help_text=_("An alternate URL to redirect to after form submission"))
    status = models.IntegerField(_("Status"), choices=STATUS_CHOICES,
        default=STATUS_PUBLISHED)
    publish_date = models.DateTimeField(_("Published from"),
        help_text=_("With published selected, won't be shown until this time"),
        blank=True, null=True)
    expiry_date = models.DateTimeField(_("Expires on"),
        help_text=_("With published selected, won't be shown after this time"),
        blank=True, null=True)
    login_required = models.BooleanField(_("Login required"), default=True,
        help_text=_("If checked, only logged in users can view the form"))
    send_email = models.BooleanField(_("Send email"), default=True, help_text=
        _("If checked, the person entering the form will be sent an email"))
    email_from = models.EmailField(_("From address"), blank=True,
        help_text=_("The address the email will be sent from"))
    email_copies = models.CharField(_("Send copies to"), blank=True,
        help_text=_("One or more email addresses, separated by commas"),
        max_length=200)
    email_subject = models.CharField(_("Subject"), max_length=200, blank=True)
    email_message = models.TextField(_("Message"), blank=True)

    objects = FormManager()

    class Meta:
        verbose_name = _("Form")
        verbose_name_plural = _("Forms")
        abstract = True

    def __str__(self):
        return str(self.title)

    def save(self, *args, **kwargs):
        """
        Create a unique slug from title - append an index and increment if it
        already exists.
        """
        if not self.slug:
            slug = slugify(self)
            self.slug = unique_slug(self.__class__.objects, "slug", slug)
        super(AbstractForm, self).save(*args, **kwargs)

    def total_entries(self):
        """
        Called by the admin list view where the queryset is annotated
        with the number of entries.
        """
        return self.total_entries
    total_entries.admin_order_field = "total_entries"

    @models.permalink
    def get_absolute_url(self):
        key = "slug" if wrapper_settings.USE_SLUGS else "form_id"
        return ("forms:form_detail", (), {key: self.get_url_attr()})

    def get_url_attr(self):
        """
        Return self.slug if wrapper_settings.USE_SLUGS is True or self.id if otherwise
        """
        if wrapper_settings.USE_SLUGS:
            return self.slug
        else:
            return self.id

    def admin_links(self):
        kw = {"args": (self.id,)}
        links = [
            (_("View form on site"), self.get_absolute_url()),
            (_("Filter entries"), reverse("admin:form_entries", **kw)),
            (_("View all entries"), reverse("admin:form_entries_show", **kw)),
            (_("Export all entries"), reverse("admin:form_entries_export", **kw)),
        ]
        for i, (text, url) in enumerate(links):
            links[i] = "<a href='%s'>%s</a>" % (url, ugettext(text))
        return "<br>".join(links)
    admin_links.allow_tags = True
    admin_links.short_description = ""


class FieldManager(models.Manager):
    """
    Only show visible fields when displaying actual form..
    """
    def visible(self):
        return self.filter(visible=True)


@python_2_unicode_compatible
class AbstractField(models.Model):
    """
    A field for a user-built form.
    """

    label = models.CharField(_("Label"), max_length=settings.LABEL_MAX_LENGTH)
    slug = models.SlugField(_('Slug'), max_length=100, blank=True,
            default="")
    field_type = models.IntegerField(_("Type"), choices=fields.NAMES)
    required = models.BooleanField(_("Required"), default=True)
    visible = models.BooleanField(_("Visible"), default=True)
    choices = models.CharField(_("Choices"), max_length=settings.CHOICES_MAX_LENGTH, blank=True,
        help_text="Comma separated options where applicable. If an option "
            "itself contains commas, surround the option starting with the %s"
            "character and ending with the %s character." %
                (settings.CHOICES_QUOTE, settings.CHOICES_UNQUOTE))
    default = models.CharField(_("Default value"), blank=True,
        max_length=settings.FIELD_MAX_LENGTH)
    placeholder_text = models.CharField(_("Placeholder Text"), null=True,
        blank=True, max_length=100, editable=settings.USE_HTML5)
    help_text = models.CharField(_("Help text"), blank=True, max_length=settings.HELPTEXT_MAX_LENGTH)

    objects = FieldManager()

    class Meta:
        verbose_name = _("Field")
        verbose_name_plural = _("Fields")
        abstract = True

    def __str__(self):
        return str(self.label)

    def get_choices(self):
        """
        Parse a choice string separated by ``wrapper_settings.CHOICES_SEPARATOR`` into a list of choices taking
        into account quoted choices using the ``settings.CHOICES_QUOTE`` and
        ``settings.CHOICES_UNQUOTE`` settings.
        """
        choice = ""
        quoted = False
        for char in self.choices:
            if not quoted and char == settings.CHOICES_QUOTE:
                quoted = True
            elif quoted and char == settings.CHOICES_UNQUOTE:
                quoted = False
            elif char == wrapper_settings.CHOICES_SEPARATOR and not quoted:
                choice = choice.strip()
                if choice:
                    yield choice, choice
                choice = ""
            else:
                choice += char
        choice = choice.strip()
        if choice:
            yield choice, choice

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self).replace('-', '_')
            self.slug = unique_slug(self.form.fields, "slug", slug)
        return super(AbstractField, self).save(*args, **kwargs)

    def is_a(self, *args):
        """
        Helper that returns True if the field's type is given in any arg.
        """
        return self.field_type in args


class AbstractFormEntry(models.Model):
    """
    An entry submitted via a user-built form.
    """

    entry_time = models.DateTimeField(_("Date/time"))

    class Meta:
        verbose_name = _("Form entry")
        verbose_name_plural = _("Form entries")
        abstract = True


class AbstractFieldEntry(models.Model):
    """
    A single field value for a form entry submitted via a user-built form.
    """

    field_id = models.IntegerField()
    value = models.CharField(max_length=settings.FIELD_MAX_LENGTH,
            null=True)

    class Meta:
        verbose_name = _("Form field entry")
        verbose_name_plural = _("Form field entries")
        abstract = True


###################################################
#                                                 #
#   Default concrete implementations are below.   #
#                                                 #
###################################################

class FormEntry(AbstractFormEntry):
    form = models.ForeignKey("Form", related_name="entries")
    # Link to user model in order to easily get user information
    submitter = models.ForeignKey(django_settings.AUTH_USER_MODEL, related_name="form_entries",
                                  null=True, blank=True, editable=False)

    def save(self, *args, **kwargs):
        # When login_required is specified as True for the form, the a submitter must be specified.
        if self.form.login_required and self.submitter is None:
            raise ValidationError(_("Login for this form is required but submitter field is empty."))
        super(FormEntry, self).save(*args, **kwargs)


class FieldEntry(AbstractFieldEntry):
    entry = models.ForeignKey("FormEntry", related_name="fields")


class Form(AbstractForm):
    # Fields to add optional capability to link form to any model
    content_type = models.ForeignKey(ContentType, null=True, blank=True, editable=False)
    object_id = models.PositiveIntegerField(null=True, blank=True, editable=False)
    content_object = GenericForeignKey()
    is_primary = models.BooleanField(_("Primary form?"), default=False,
                                     help_text=_("Is this the primary form for this object?"))

    def save(self, *args, **kwargs):
        """Make sure that only one primary form exists per object."""
        if self.is_primary is True:
            # Make sure there is no other primary form related to the same object
            object_forms = Form.objects.filter(content_type=self.content_type, object_id=self.object_id)
            object_forms.update(is_primary=False)
        super(Form, self).save(*args, **kwargs)


class Field(AbstractField):
    """
    Implements automated field ordering.
    """

    form = models.ForeignKey("Form", related_name="fields")
    order = models.IntegerField(_("Order"), null=True, blank=True)

    class Meta(AbstractField.Meta):
        ordering = ("order",)

    def save(self, *args, **kwargs):
        if self.order is None:
            self.order = self.form.fields.count()
        super(Field, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        fields_after = self.form.fields.filter(order__gte=self.order)
        fields_after.update(order=models.F("order") - 1)
        super(Field, self).delete(*args, **kwargs)
