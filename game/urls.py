from django.urls import path
from . import views
 #######test#####
from django.contrib.auth import views as auth_views

urlpatterns = [
 #######test#####
    path('', views.main_page, name='main'), #기본 루트 연결
    path('start/', views.start_game, name='start_game'),     # 구현 예정
    path('list/', views.game_list, name='game_list'),        # 구현 예정
    path('detail/<int:pk>/', views.game_detail, name='game_detail'), # 게임 상세
    path('ranking/', views.ranking_page, name='ranking'),    # 구현 예정
    path('login/', auth_views.LoginView.as_view(template_name='games/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    
    ######test#####
]