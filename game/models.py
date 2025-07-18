from django.db import models
from django.contrib.auth.models import User

from django.contrib.auth.models import User



class Game(models.Model):
    attacker = models.ForeignKey(User, related_name='attacker_games', on_delete=models.CASCADE)
    defender = models.ForeignKey(User, related_name='defender_games', on_delete=models.CASCADE)
    attacker_card = models.IntegerField()
    defender_card = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('진행중', '진행중'), ('반격대기', '반격대기'), ('종료', '종료')])
    result = models.CharField(max_length=20, choices=[('승리', '승리'), ('패배', '패배'), ('무승부', '무승부')], null=True, blank=True)
    card_rule = models.CharField(max_length=10, choices=[('high', 'high'), ('low', 'low')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        try:
            attacker_name = str(self.attacker) if self.attacker else 'Unknown'
            defender_name = str(self.defender) if self.defender else 'Unknown'
            return f"{attacker_name} VS {defender_name} ({self.status})"
        except Exception as e:
            raise Exception('Game 모델의 __str__에서 예외 발생') from e