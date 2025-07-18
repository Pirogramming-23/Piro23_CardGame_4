from django.shortcuts import render,redirect
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm

try:
    from .models import Game
except ImportError as e:
    raise ImportError('Game 모델 임포트 실패: makemigrations 및 migrate가 정상적으로 수행되었는지 확인하세요.') from e
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import Http404
from .forms import GameStartForm, CounterAttackForm
import random

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


####### test ########

@login_required
def start_game(request):
    if request.method == 'POST':
        form = GameStartForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                card = int(form.cleaned_data['card'])
                opponent = form.cleaned_data['opponent']
                rule = random.choice(['high', 'low'])
                game = Game.objects.create(
                    attacker=request.user,
                    defender=opponent,
                    attacker_card=card,
                    status='진행중',  # 생성 시 '진행중'으로 저장
                    card_rule=rule
                )
                return redirect('game_list')
            except Exception as e:
                raise Exception('게임 생성 중 오류 발생') from e
    else:
        form = GameStartForm(user=request.user)
    return render(request, 'games/start.html', {'form': form})

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

    # 수비자가 상세 페이지에 진입하면 '반격대기'로 변경
    if game.status == '진행중' and request.user == game.defender:
        game.status = '반격대기'
        game.save()

    session_key = f'counter_choices_{game.pk}'
    # 게임 취소 처리 (공격자만, 진행중 상태에서)
    if request.method == 'POST' and game.status == '진행중' and request.user == game.attacker:
        try:
            game.delete()
            return redirect('game_list')
        except Exception as e:
            raise Exception('게임 취소 중 오류 발생') from e

    # CounterAttack 처리
    if request.method == 'POST' and game.status == '반격대기' and request.user == game.defender:
        card_choices = request.session.get(session_key)
        form = CounterAttackForm(request.POST, card_choices=card_choices)
        if form.is_valid():
            try:
                defender_card = int(form.cleaned_data['card'])
                game.defender_card = defender_card
                # 결과 결정
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
        # GET: 랜덤 5개 뽑아서 세션에 저장
        card_choices = random.sample(range(1, 11), 5)
        request.session[session_key] = card_choices
        form = CounterAttackForm(card_choices=card_choices)

    return render(request, 'games/detail.html', {'game': game, 'user': request.user, 'counter_form': form})

@login_required
def ranking_page(request):
    # 유저별 누적 점수 계산
    users = User.objects.all()
    ranking = []
    for user in users:
        win_score = Game.objects.filter(attacker=user, result='승리').aggregate(s=Sum('attacker_card'))['s'] or 0
        lose_score = Game.objects.filter(attacker=user, result='패배').aggregate(s=Sum('attacker_card'))['s'] or 0
        win_score += Game.objects.filter(defender=user, result='승리').aggregate(s=Sum('defender_card'))['s'] or 0
        lose_score += Game.objects.filter(defender=user, result='패배').aggregate(s=Sum('defender_card'))['s'] or 0
        total = win_score - lose_score
        ranking.append({'user': user, 'score': total})
    ranking = sorted(ranking, key=lambda x: x['score'], reverse=True)
    return render(request, 'games/ranking.html', {'ranking': ranking})


def custom_logout(request):
    logout(request)
    return redirect('/')
