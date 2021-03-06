from django import forms
from django.contrib.auth.models import User

from accounts.models import CommonProfile
from clubs.models import english_city_choices
from core.models import StudentClubYear
from researchhub import utils
from researchhub.models import Supervisor, Project, SkilledStudent, Domain, Skill
from userena.forms import SignupForm

Did_you_get_benefit_from_ReserachHub = (
    ('','Choose'),
    ('Yes','Yes'),
    ('No','No')
)

class FeedbackForm(forms.Form):
    get_benefit = forms.CharField(label="Did you get benefit from ResearchHub?",
                                        max_length=20,widget=forms.Select(choices=Did_you_get_benefit_from_ReserachHub))
    why = forms.CharField(label="Why?",widget=forms.Textarea)

class ConsultationForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea)
    first_date = forms.DateField()
    second_date = forms.DateField()

class EmailForm(forms.Form):
    text = forms.CharField(label="Wtite your message here",widget=forms.Textarea)

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['supervisor', 'field', 'title', 'description',
                  'required_role', 'prerequisites', 'duration',
                  'communication']

class MemberProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['supervisor', 'field', 'title', 'description',
                  'required_role', 'prerequisites', 'duration',
                  'communication', 'is_personal']

class AddSupervisorForm(forms.ModelForm):
    class Meta:
        model = Supervisor
        fields = ['user', 'avatar', 'domain', 'interests',
                  'communication', 'is_hidden', 'available_from',
                  'available_until']

class EditSupervisorForm(forms.ModelForm):
    class Meta:
        model = Supervisor
        fields = ['avatar', 'domain', 'interests',
                  'communication', 'is_hidden', 'available_from',
                  'available_until']

class SkilledStudentForm(forms.ModelForm):
    class Meta:
        model = SkilledStudent
        fields = ['skills','description', 'fields_of_interest', 'previous_experience',
                  'ongoing_projects', 'condition', 'available_until']

class ResearchHubSignupForm(SignupForm):
    en_first_name = forms.CharField(max_length=30)
    en_middle_name = forms.CharField(max_length=30)
    en_last_name = forms.CharField(max_length=30)
    badge_number = forms.IntegerField(required=False)
    job_description = forms.CharField(widget=forms.Textarea)
    #specialty = forms.CharField(max_length=100)
    domain = forms.IntegerField()
    interests = forms.CharField(widget=forms.Textarea)
    communication = forms.CharField(widget=forms.Textarea)
    #available_from = forms.DateField(required=False)
    #available_until = forms.DateField(required=False)
    city = forms.CharField(max_length=20,
                           widget=forms.Select(choices=english_city_choices))

    def __init__(self, *args, **kw):
        super(ResearchHubSignupForm, self).__init__(*args, **kw)
        # We don't want usernames (We could have inherited userena's
        # SignupFormOnlyEmail, but it's more tricky to modify.)
        del self.fields['username']

        domain_choices = []
        for domain in Domain.objects.all():
            domain_choices.append((domain.pk, domain.name))
        self.fields['domain'].widget = forms.Select(choices=domain_choices)

    def clean(self):
        # Call the parent class's clean function.
        cleaned_data = super(ResearchHubSignupForm, self).clean()

        # Remove spaces at the start and end of all text fields.
        for field in cleaned_data:
            if isinstance(cleaned_data[field], unicode):
                cleaned_data[field] = cleaned_data[field].strip()

        return cleaned_data

    def save(self):
        # All username names should be lower-case.
        self.cleaned_data['email'] = self.cleaned_data['email'].lower()
        self.cleaned_data['username'] = self.cleaned_data['email'].split('@')[0]
        self.cleaned_data['username'] = self.cleaned_data['username']

        domain_pk = self.cleaned_data['domain']
        domain = Domain.objects.get(pk=domain_pk)
        new_user = super(ResearchHubSignupForm, self).save()
        current_year = StudentClubYear.objects.get_current()
        CommonProfile.objects.create(user=new_user,
                                     is_student=False,
                                     en_first_name=self.cleaned_data['en_first_name'],
                                     en_middle_name=self.cleaned_data['en_middle_name'],
                                     en_last_name=self.cleaned_data['en_last_name'],
                                     badge_number=self.cleaned_data['badge_number'],
                                     city=self.cleaned_data['city'],
                                     job_description=self.cleaned_data['job_description'],
                                     college=None,
                                     student_id=None)
        Supervisor.objects.create(user=new_user,
                                  year=current_year,
                                  interests=self.cleaned_data['interests'],
                                  communication=self.cleaned_data['communication'],
                                  #specialty=self.cleaned_data['specialty'],
                                  #available_from=self.cleaned_data.get('available_from'),
                                  #available_until=self.cleaned_data.get('available_until'),
                                  domain=domain)
        return new_user
