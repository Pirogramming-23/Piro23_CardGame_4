import random
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.http import Http404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Game
from .forms import GameStartForm, CounterAttackForm

from django.contrib.auth import get_user_model

User = get_user_model()



def main_page(request):
    return render(request, 'games/main.html')


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
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
    attacker = game.attacker.profile
    defender = game.defender.profile
    bet = game.bet_point

    if result == '승리':
        attacker.point += bet
        defender.point -= bet
    elif result == '패배':
        attacker.point -= bet
        defender.point += bet
    # 무승부는 변화 없음

    attacker.save()
    defender.save()

    # 게임 정보 저장
    game.defender_card = defender_card
    game.result = result
    game.status = '종료'
    game.save()
    return result

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
                result = process_counter_attack(game, defender_card)
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

    attacker_point = getattr(game.attacker.profile, 'point', 0)
    defender_point = getattr(game.defender.profile, 'point', 0)

    return render(request, 'games/detail.html', {
        'game': game,
        'user': request.user,
        'counter_form': form,
        'attacker_point': attacker_point,
        'defender_point': defender_point
    })


@login_required
def ranking_page(request):
    users = User.objects.all()
    ranking = []

    for user in users:
        try:
            point = user.profile.point
        except:
            point = 0

        ranking.append({
            'user': user,
            'score': point  # score에 profile.point를 바로 씀
        })

    # 정렬 (포인트 기준)
    ranking = sorted(ranking, key=lambda x: x['score'], reverse=True)

    # 막대 height 계산
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
            bet_point = int(form.cleaned_data['bet_point'])
            rule = random.choice(['high', 'low'])

        # 내 포인트 부족하면 예외 처리
        if request.user.profile.point < bet_point:
            form.add_error(None, '보유 포인트가 부족합니다.')
            return render(request, 'games/start.html', {'form': form})

        # 상대방도 베팅 받을 수 있는 포인트 있어야 함
        if opponent.profile.point < bet_point:
            form.add_error(None, f'상대방({opponent.username})의 포인트가 부족합니다.')
            return render(request, 'games/start.html', {'form': form})

        Game.objects.create(
            attacker=request.user,
            defender=opponent,
            attacker_card=card,
            status='진행중',
            card_rule=rule,
            bet_point=bet_point
        )
        return redirect('game_list')
