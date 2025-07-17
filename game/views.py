from django.shortcuts import render,redirect
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