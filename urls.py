from django.conf.urls import patterns, include, url
from django.contrib import admin
from app.views import *

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'freesage.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^/?$', AppLandingView.as_view()),
    url(r'^explore/?$', AppLandingView.as_view()),
    url(r'^properties/?([0-9]+)?$', PropertiesView.as_view()),
    url(r'^propertyMetas/?([0-9]+)?$', PropertyMetasView.as_view()),
    url(r'^propertyStatuses/?([0-9]+)?$', PropertyStatusView.as_view()),
    url(r'^propertyMeta/?$', PropertyMetaView.as_view()),
)
