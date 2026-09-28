from django.db import migrations, models

SEED_USERS = [
    ('student', '1234'),
    ('admin', 'rootpass'),
    ('teacher', 'teacher123'),
]


def seed_users(apps, schema_editor):
    Auth = apps.get_model('training', 'Auth')
    for user_id, password in SEED_USERS:
        Auth.objects.create(user_id=user_id, password=password)


def unseed_users(apps, schema_editor):
    Auth = apps.get_model('training', 'Auth')
    Auth.objects.filter(user_id__in=[u for u, _ in SEED_USERS]).delete()


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Auth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=100)),
            ],
        ),
        migrations.RunPython(seed_users, unseed_users),
    ]
