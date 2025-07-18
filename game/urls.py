from django.urls import path
from . import views
from .views import StartGameView

urlpatterns = [
    path('', views.main_page, name='main'), #기본 루트 연결
    path('start/', StartGameView.as_view(), name='start_game'),     # 구현 예정
    path('list/', views.game_list, name='game_list'),        # 구현 예정
    path('ranking/', views.ranking_page, name='ranking'),    # 구현 예정
]