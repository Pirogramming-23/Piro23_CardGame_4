from django import forms
from django.contrib.auth.models import User
import random

class GameCreateForm(forms.Form):
    # 숫자 카드 선택 필드 (랜덤 5개 중 1개 선택)
    card = forms.ChoiceField(choices=[])

     # 상대 유저 선택 필드 (본인을 제외한 유저들)
    target_user = forms.ModelChoiceField(queryset=User.objects.none())

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)  # 로그인 유저
        cards = kwargs.pop('cards', [])   # 랜덤 카드 리스트
        super().__init__(*args, **kwargs)

        # 카드 옵션 설정
        if cards:
            self.fields['card'].choices = [(num, str(num)) for num in cards]

        # 선택 가능한 유저 설정 (자기 자신 제외)
        if current_user:
            self.fields['target_user'].queryset = User.objects.exclude(id=current_user.id)