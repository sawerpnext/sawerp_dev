from django.contrib import admin
from django.urls import path, include

# --- THIS IS THE FIX ---
# You must import the view you are trying to use
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # This line is correct, as your app is 'operations'
    path("api/", include("operations.urls")), 
    
    # This was the line causing the crash. 
    # I've also changed the path to be '/api/token-auth/' 
    # to keep all your API URLs together.
    path("api/token-auth/", obtain_auth_token, name="api_token_auth"),
]