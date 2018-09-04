from django.conf.urls import url
from django.contrib import admin
from api import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/links/(?P<url>.+)$', views.check_url_get_links),
    url(r'^api/text/(?P<url>.+)$', views.check_url_get_text),
    url(r'^api/(?P<url>.+)$', views.check_url),

]
