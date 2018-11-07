from django.conf.urls import url
from django.contrib import admin
from api import views


urlpatterns = [
    url(r'^api/lexrank/$', views.lexrank),
    url(r'^api/textteaser/$', views.textteaser),
    url(r'^api/textrank/$', views.textrank),
    url(r'^admin/', admin.site.urls),
    url(r'^api/goosetext/(?P<url>.+)$', views.goose_get_text),
    url(r'^api/links/(?P<url>.+)$', views.check_url_get_links),
    url(r'^api/text/(?P<url>.+)$', views.check_url_get_text),
    url(r'^api/search/(?P<concept>.+)$', views.google_search),
    url(r'^api/(?P<url>.+)$', views.check_url),
    url(r'^api/$', views.index),
]
