import random
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from django.http import Http404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Game
from .forms import GameStartForm, CounterAttackForm


def main_page(request):
    return render(request, 'games/main.html')


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'games/signup.html', {'form': form})


@login_required
def game_list(request):
    user = request.user
    games = Game.objects.filter(attacker=user) | Game.objects.filter(defender=user)
    games = games.order_by('-created_at')
    return render(request, 'games/list.html', {'games': games, 'user': user})


@login_required
def game_detail(request, pk):
    try:
        game = Game.objects.get(pk=pk)
    except Game.DoesNotExist as e:
        raise Http404('해당 게임이 존재하지 않습니다.') from e

    # 수비자 진입 시 상태 변경
    if game.status == '진행중' and request.user == game.defender:
        game.status = '반격대기'
        game.save()

    session_key = f'counter_choices_{game.pk}'

    # 공격자 취소 처리
    if request.method == 'POST' and game.status == '진행중' and request.user == game.attacker:
        try:
            game.delete()
            return redirect('game_list')
        except Exception as e:
            raise Exception('게임 취소 중 오류 발생') from e

    # 수비자 반격 처리
    if request.method == 'POST' and game.status == '반격대기' and request.user == game.defender:
        card_choices = request.session.get(session_key)
        form = CounterAttackForm(request.POST, card_choices=card_choices)
        if form.is_valid():
            try:
                defender_card = int(form.cleaned_data['card'])
                game.defender_card = defender_card

                # 결과 판정
                if game.card_rule == 'high':
                    if game.attacker_card > defender_card:
                        game.result = '승리'
                    elif game.attacker_card < defender_card:
                        game.result = '패배'
                    else:
                        game.result = '무승부'
                else:  # low
                    if game.attacker_card < defender_card:
                        game.result = '승리'
                    elif game.attacker_card > defender_card:
                        game.result = '패배'
                    else:
                        game.result = '무승부'

                game.status = '종료'
                game.save()
                if session_key in request.session:
                    del request.session[session_key]
                return redirect('game_detail', pk=game.pk)
            except Exception as e:
                raise Exception('CounterAttack 처리 중 오류 발생') from e
    else:
        # GET: 랜덤 5개 세션 저장
        card_choices = random.sample(range(1, 11), 5)
        request.session[session_key] = card_choices
        form = CounterAttackForm(card_choices=card_choices)

    return render(request, 'games/detail.html', {
        'game': game,
        'user': request.user,
        'counter_form': form
    })


@login_required
def ranking_page(request):
    users = User.objects.all()
    ranking = []
    for user in users:
        # 공격자 승리(공격자 입장에서만 '승리'로 저장됨)
        attacker_win = Game.objects.filter(attacker=user, result='승리').count()
        # 수비자 승리(수비자는 공격자가 '패배'로 저장된 게임에서 승리)
        defender_win = Game.objects.filter(defender=user, result='패배').count()
        # 공격자 패배(공격자 입장에서만 '패배'로 저장됨)
        attacker_lose = Game.objects.filter(attacker=user, result='패배').count()
        # 수비자 패배(수비자는 공격자가 '승리'로 저장된 게임에서 패배)
        defender_lose = Game.objects.filter(defender=user, result='승리').count()
        total = (attacker_win + defender_win) - (attacker_lose + defender_lose)
        ranking.append({'user': user, 'score': total})
    ranking = sorted(ranking, key=lambda x: x['score'], reverse=True)
    return render(request, 'games/ranking.html', {'ranking': ranking})

def custom_logout(request):
    logout(request)
    return redirect('/')


# 클래스형 게임 생성 뷰 (start_game 함수형 뷰는 제거됨)
class StartGameView(LoginRequiredMixin, View):
    def get(self, request):
        random_cards = random.sample(range(1, 11), 5)
        request.session['random_cards'] = random_cards
        form = GameStartForm(current_user=request.user, card_choices=random_cards)
        return render(request, 'games/start.html', {'form': form})

    def post(self, request):
        random_cards = request.session.get('random_cards', [])
        form = GameStartForm(request.POST, current_user=request.user, card_choices=random_cards)
        if form.is_valid():
            card = int(form.cleaned_data['card'])
            opponent = form.cleaned_data['opponent']
            rule = random.choice(['high', 'low'])
            Game.objects.create(
                attacker=request.user,
                defender=opponent,
                attacker_card=card,
                status='진행중',
                card_rule=rule
            )
            return redirect('game_list')
        return render(request, 'games/start.html', {'form': form})
