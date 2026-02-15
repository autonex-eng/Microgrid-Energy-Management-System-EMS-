from django.contrib import admin
from django.urls import path
from core.views import dashboard_view, get_live_data, update_house_data

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # The User Interface
    path('', dashboard_view, name='dashboard'),
    
    # The API Endpoints
    path('api/data/', get_live_data, name='get_data'),     # Frontend polls this
    path('api/update/', update_house_data, name='update'), # Simulator/ESP sends to this
]