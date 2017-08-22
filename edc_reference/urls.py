from django.conf.urls import url

from .admin_site import edc_reference_admin
from .views import HomeView

app_name = 'edc_reference'

urlpatterns = [
    url(r'^admin/', edc_reference_admin.urls),
    url(r'', HomeView.as_view(), name='home_url'),
]
