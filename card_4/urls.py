from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from game import views
from django.conf import settings
from django.conf.urls.static import static

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
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)