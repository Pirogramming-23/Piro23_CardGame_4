from django.db import models
from django.contrib.auth.models import User

class Game(models.Model):
    # 공격자 (게임을 생성한 유저)
    attacker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_started')
    
    # 수비자 (공격 대상 유저)
    defender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_received')
    
    # 공격자가 낸 숫자 카드 (1~10)
    attacker_card = models.IntegerField()
    
    # 수비자가 낸 숫자 카드 (반격 시 사용, 선택 전엔 null)
    defender_card = models.IntegerField(null=True, blank=True)
    
    # 게임 생성 시간
    created_at = models.DateTimeField(auto_now_add=True)
    
    # 반격 완료 여부 (False면 아직 반격 안 함)
    is_completed = models.BooleanField(default=False)
    
    # 게임 결과 (win / lose / draw)
    result = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f"{self.attacker} vs {self.defender}"
