"""
URL configuration for card_4 project.

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
from django.urls import path, include
from django.contrib.auth import views as auth_views
from game import views
urlpatterns = [
    path('', include('game.urls')),
    path('admin/', admin.site.urls),
    path('signup/', views.signup, name='signup'),  # 회원가입
    path('accounts/login/', auth_views.LoginView.as_view(  
        template_name='games/login.html',
        redirect_authenticated_user=True,
        next_page='main'
    ), name='login'),
    path('accounts/logout/', views.custom_logout, name='logout'), # 메인페이지 logout 경로설정
]