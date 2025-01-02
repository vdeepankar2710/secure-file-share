"""
URL configuration for secureFileShare project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from users.views import VerifyOTPView, LoginView, LogoutView, RegisterView
from fileManagement.views import FileUploadView, FileDownloadView, GenerateSecureLinkView, SecureFileDownloadView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/register/', RegisterView.as_view(), name='register_user'),
    path('user/verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('user/login/', LoginView.as_view(), name='login'),
    path('user/logout/', LogoutView.as_view(), name='logout'),
    path('file/upload/', FileUploadView.as_view(), name='file_upload'),
    path('file/download/<int:file_id>/', FileDownloadView.as_view(), name='file_download'),
    path('secure-link/<int:file_id>/', GenerateSecureLinkView.as_view(), name='generate_secure_link'),
    path('download/<int:file_id>/<int:expiration_time>/<str:signature>/', SecureFileDownloadView.as_view(), name='secure_file_download'),
]
