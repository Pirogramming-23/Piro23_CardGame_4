from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

# CustomUser 모델 가져오기
from .models import CustomUser

User = get_user_model()

BET_CHOICES = [(50, '50'), (100, '100'), (150, '150'), (200, '200')]


class GameStartForm(forms.Form):
    card = forms.ChoiceField(label='카드 선택', widget=forms.RadioSelect)
    opponent = forms.ModelChoiceField(queryset=User.objects.none(), label='상대 선택')
    bet_point = forms.ChoiceField(choices=BET_CHOICES, label='베팅 점수')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('current_user', None)
        card_choices = kwargs.pop('card_choices', None)
        super().__init__(*args, **kwargs)

        if card_choices is None:
            from random import sample
            card_choices = sample(range(1, 11), 5)
        self.fields['card'].choices = [(c, str(c)) for c in card_choices]

        if user:
            self.fields['opponent'].queryset = User.objects.exclude(id=user.id)
        else:
            self.fields['opponent'].queryset = User.objects.all()


class CounterAttackForm(forms.Form):
    card = forms.ChoiceField(label='카드 선택', widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        card_choices = kwargs.pop('card_choices', None)
        super().__init__(*args, **kwargs)
        if card_choices:
            self.fields['card'].choices = [(c, str(c)) for c in card_choices]
        else:
            self.fields['card'].choices = [(i, str(i)) for i in range(1, 11)]


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email')
