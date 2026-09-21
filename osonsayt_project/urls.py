from django.contrib import admin
from django.urls import path, re_path, include
from core import views
from core.models import LegalPage
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', views.home, name='home'),
    re_path(r'^(?P<slug>%s)/$' % '|'.join(slug for slug, _ in LegalPage.SLUG_CHOICES), views.legal_page, name='legal_page'),
    path('submit-lead/', views.submit_lead, name='submit_lead'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
