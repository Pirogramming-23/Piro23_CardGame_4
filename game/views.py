import random
from django.shortcuts import render,redirect
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import GameCreateForm
from .models import Game

def main_page(request):
    return render(request, 'games/main.html') #메인 페이지 뷰 함수 추가

#회원가입뷰 추가
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # 회원가입 후 로그인 페이지로 이동
    else:
        form = UserCreationForm()
    return render(request, 'games/signup.html', {'form': form})

def start_game(request):
    return render(request, 'games/start.html')  # 게임 생성 (공격 시작) 페이지

def game_list(request):
    return render(request, 'games/list.html') #게임 전적 / 게임 리스트 페이지

def ranking_page(request):
    return render(request, 'games/ranking.html') #유저 랭킹(보기) 페이지(모든 유저를 누적 점수 순으로 정렬해서 표시)

def custom_logout(request):
    logout(request)
    return redirect('/')


# 게임 생성 뷰 (카드 선택 + 유저 선택 → 게임 생성)
class StartGameView(LoginRequiredMixin, View):
    def get(self, request):
        # 랜덤 카드 5장 생성 (1~10)
        random_cards = random.sample(range(1, 11), 5)
        request.session['random_cards'] = random_cards  # 세션에 저장
        
        # 폼 생성 (현재 유저, 카드 리스트 전달)
        form = GameCreateForm(current_user=request.user, cards=random_cards)
        return render(request, 'games/start.html', {'form': form})

    def post(self, request):
        # 세션에서 카드 목록 불러오기
        random_cards = request.session.get('random_cards', [])
        form = GameCreateForm(request.POST, current_user=request.user, cards=random_cards)
        if form.is_valid():
            # 카드, 상대 유저 가져오기
            card = int(form.cleaned_data['card'])
            target_user = form.cleaned_data['target_user']

            # 게임 객체 생성
            Game.objects.create(
                attacker=request.user,
                defender=target_user,
                attacker_card=card
            )
            return redirect('game_list') # 게임 목록으로 이동
        return render(request, 'games/start.html', {'form': form})