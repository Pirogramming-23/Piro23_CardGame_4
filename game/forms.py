from django import forms
from django.contrib.auth.models import User
import random

CARD_CHOICES = [(i, str(i)) for i in range(1, 11)]

class GameStartForm(forms.Form):
    card = forms.ChoiceField(choices=[], label='카드 선택', widget=forms.RadioSelect)
    opponent = forms.ModelChoiceField(queryset=User.objects.none(), label='상대 선택')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # 카드 1~10 중 랜덤 5개 제공
        cards = random.sample(range(1, 11), 5)
        self.fields['card'].choices = [(c, str(c)) for c in cards]
        # 본인 제외 유저만 상대 선택
        if user:
            self.fields['opponent'].queryset = User.objects.exclude(id=user.id)
        else:
            self.fields['opponent'].queryset = User.objects.all()

class CounterAttackForm(forms.Form):
    card = forms.ChoiceField(choices=[], label='카드 선택', widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        card_choices = kwargs.pop('card_choices', None)
        super().__init__(*args, **kwargs)
        if card_choices:
            self.fields['card'].choices = [(c, str(c)) for c in card_choices]
        else:
            self.fields['card'].choices = [(i, str(i)) for i in range(1, 11)]
