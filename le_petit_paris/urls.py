from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def redirect_to_login(request):
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_login, name='home'),  # Redirection vers login
    path('production/', include('production.urls')), # Préfixe pour l'app production
]