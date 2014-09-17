from django.conf.urls import patterns, include, url
from django.contrib import admin
from app.views import *

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'freesage.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^explore/?$', AppLandingView.as_view()),
)
