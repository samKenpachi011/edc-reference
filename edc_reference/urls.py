from django.views.generic.base import RedirectView
from django.urls.conf import path

from .admin_site import edc_reference_admin
# from .views import HomeView

app_name = 'edc_reference'

urlpatterns = [
    path('admin/edc_reference/', edc_reference_admin.urls),
    path('admin/', edc_reference_admin.urls),
    # path('', HomeView.as_view(), name='home_url'),
    path('', RedirectView.as_view(url='admin/edc_reference/'), name='home_url'),
]
