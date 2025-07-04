"""
URL configuration for image_stegno project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from stegno_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_login,name='index_login'),
    path('encryption/', views.encryption_view,name='encryption'),
    path('encryption_AES/', views.encryption_AES,name='encryption_AES'),
    path('decryption/', views.decryption_view,name='decryption'),
    path('decryption_AES/', views.decryption_AES,name='decryption_AES'),
    path('signup/',views.send_otp_email,name='signup'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('welcome/', views.welcome, name='welcome'),
    path('howitworks/', views.howitworks, name='howitworks'),
    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
