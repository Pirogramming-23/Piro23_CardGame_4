import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attacker_card', models.IntegerField()),
                ('defender_card', models.IntegerField(blank=True, null=True)),
                ('status', models.CharField(choices=[('진행중', '진행중'), ('반격대기', '반격대기'), ('종료', '종료')], max_length=20)),
                ('result', models.CharField(blank=True, choices=[('승리', '승리'), ('패배', '패배'), ('무승부', '무승부')], max_length=20, null=True)),
                ('card_rule', models.CharField(choices=[('high', 'high'), ('low', 'low')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('attacker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attacker_games', to=settings.AUTH_USER_MODEL)),
                ('defender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='defender_games', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
