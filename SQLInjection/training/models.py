from django.db import models


class Auth(models.Model):
    # 테이블명: training_auth (id, user_id, password)
    # 교육용이므로 비밀번호를 평문으로 저장한다. 실제 서비스에서는 반드시 해시로 저장할 것.
    user_id = models.CharField(max_length=50)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.user_id
