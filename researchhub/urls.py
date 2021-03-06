from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from researchhub import views

urlpatterns = patterns('',
    url(r'^$', views.index, name="index"),
    url(r'^indicators/$', views.indicators, name="indicators"),
    url(r'^faq/$', TemplateView.as_view(template_name='researchhub/faq.html'), name="faq"),
    url(r'^how_it_works/$', TemplateView.as_view(template_name='researchhub/how_it_works.html'), name="how_it_works"),
    url(r'^join_us/$', TemplateView.as_view(template_name='researchhub/join_us.html'), name="join_us"),
    url(r'^consultation/$', views.submit_consultation, name="submit_consultation"),
    url(r'^consultation/received/$', TemplateView.as_view(template_name='researchhub/consultation_received.html'), name="consultation_received"),
    url(r'^feedback/$', views.submit_feedback, name="submit_feedback"),

    # Projects
    url(r'^projects/$', views.list_projects, name="list_projects"),
    url(r'^projects/control/$', views.control_projects, name="control_projects"),
    url(r'^projects/add/intro/$', TemplateView.as_view(template_name='researchhub/add_project_introduction.html'), name="add_project_introduction"),
    url(r'^projects/add/$', views.add_project, name="add_project"),
    url(r'^projects/(?P<pk>\d+)/$', views.show_project, name="show_project"),
    url(r'^projects/(?P<pk>\d+)/edit/$', views.edit_project, name="edit_project"),
    url(r'^projects/(?P<pk>\d+)/delete/$', views.delete_project, name="delete_project"),

    # Supervisors
    url(r'^supervisors/domains/$', views.list_domains, name="list_domains"),
    url(r'^supervisors/domains/(?P<pk>\d+)/$', views.list_supervisors, name="list_supervisors"),
    url(r'^supervisors/control/$', views.control_supervisors, name="control_supervisors"),
    #url(r'^supervisors/invitation$', TemplateView.as_view(template_name='researchhub/invitation.html'), name="invitation"),
    url(r'^supervisors/invitation$', views.InvitationView.as_view(cmd_options = {
                'margin-top': 20,
                'margin-right': 20,
                'margin-left': 20,
            }, template_name='researchhub/invitation.html', filename='invitation.pdf'), name="invitation"),
    url(r'^supervisors/add/$', views.add_supervisor, name="add_supervisor"),
    url(r'^supervisors/(?P<pk>\d+)/$', views.show_supervisor, name="show_supervisor"),
    url(r'^supervisors/(?P<pk>\d+)/rate/$', views.rate_supervisor, name="rate_supervisor"),
    url(r'^supervisors/(?P<pk>\d+)/edit/$', views.edit_supervisor, name="edit_supervisor"),
    url(r'^supervisors/(?P<pk>\d+)/delete/$', views.delete_supervisor, name="delete_supervisor"),
    url(r'^supervisors/(?P<pk>\d+)/send_email/$', views.send_email, name="send_email"),

    # Skills
    url(r'^skills/$', views.list_skills, name="list_skills"),
    url(r'^skills/add/$', views.add_skill, name="add_skill"),
    url(r'^skills/add/intro/$', TemplateView.as_view(template_name='researchhub/add_skill_introduction.html'), name="add_skill_introduction"),
    url(r'^skills/(?P<pk>\d+)/$', views.show_skill, name="show_skill"),
    url(r'^skills/(?P<pk>\d+)/edit/$', views.edit_skill, name="edit_skill"),
    url(r'^skills/(?P<pk>\d+)/delete/$', views.delete_skill, name="delete_skill"),
)
