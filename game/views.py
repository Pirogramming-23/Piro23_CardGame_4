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


def process_counter_attack(game, defender_card):
    # 이미 반격한 게임 예외처리
    if game.status != '반격대기':
        raise Exception('이미 반격이 완료된 게임입니다.')

    # 결과 판정
    if game.card_rule == 'high':
        if game.attacker_card > defender_card:
            result = '승리'
        elif game.attacker_card < defender_card:
            result = '패배'
        else:
            result = '무승부'
    else:  # low
        if game.attacker_card < defender_card:
            result = '승리'
        elif game.attacker_card > defender_card:
            result = '패배'
        else:
            result = '무승부'

    # 점수 변화(임시 변수, DB 저장X)
    attacker_score_change = 0
    defender_score_change = 0
    if result == '승리':
        attacker_score_change = game.attacker_card
        defender_score_change = -defender_card
    elif result == '패배':
        attacker_score_change = -game.attacker_card
        defender_score_change = defender_card
    # 무승부는 변화 없음

    # 게임 정보 저장
    game.defender_card = defender_card
    game.result = result
    game.status = '종료'
    game.save()
    return result, attacker_score_change, defender_score_change


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
                # 함수 호출로 반격 처리
                result, attacker_score_change, defender_score_change = process_counter_attack(game, defender_card)
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
        attacker_win = Game.objects.filter(attacker=user, result='승리').count()
        defender_win = Game.objects.filter(defender=user, result='패배').count()
        attacker_lose = Game.objects.filter(attacker=user, result='패배').count()
        defender_lose = Game.objects.filter(defender=user, result='승리').count()
        total = (attacker_win + defender_win) - (attacker_lose + defender_lose)
        ranking.append({'user': user, 'score': total})

    # 정렬
    ranking = sorted(ranking, key=lambda x: x['score'], reverse=True)

    # 최대 점수 기준으로 height 설정 (최소 80px, 최대 220px)
    max_score = ranking[0]['score'] if ranking else 1
    for r in ranking:
        normalized = r['score'] / max_score if max_score else 0
        r['height'] = int(80 + normalized * 140)  # 최소 80, 최대 220

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
