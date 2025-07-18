from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


# 커스텀 유저 모델
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    profile_image = models.ImageField(
        upload_to='profile_images/',
        blank=True,
        null=True,
        default='logo.png'  # media/logo.png 아님!
    )

    def __str__(self):
        return self.username


# 게임 모델 (CustomUser 사용)
class Game(models.Model):
    attacker = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='attacker_games', on_delete=models.CASCADE)
    defender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='defender_games', on_delete=models.CASCADE)
    attacker_card = models.IntegerField()
    defender_card = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('진행중', '진행중'),
        ('반격대기', '반격대기'),
        ('종료', '종료')
    ])
    result = models.CharField(max_length=20, choices=[
        ('승리', '승리'),
        ('패배', '패배'),
        ('무승부', '무승부')
    ], null=True, blank=True)
    card_rule = models.CharField(max_length=10, choices=[
        ('high', 'high'),
        ('low', 'low')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    bet_point = models.IntegerField(default=50)

    def __str__(self):
        try:
            attacker_name = str(self.attacker) if self.attacker else 'Unknown'
            defender_name = str(self.defender) if self.defender else 'Unknown'
            return f"{attacker_name} VS {defender_name} ({self.status})"
        except Exception as e:
            raise Exception('Game 모델의 __str__에서 예외 발생') from e


# 프로필 모델 (CustomUser 참조)
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    point = models.IntegerField(default=500)

    def __str__(self):
        return f"{self.user.username}의 프로필"
