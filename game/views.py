from django.shortcuts import render,redirect
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
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
