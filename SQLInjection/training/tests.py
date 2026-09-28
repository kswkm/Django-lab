from django.test import TestCase
from django.urls import reverse

INJECTION = "' or '1' = '1"


class LoginViewTests(TestCase):
    def post(self, user_id, password, mode):
        return self.client.post(reverse('login'), {
            'user_id': user_id, 'password': password, 'mode': mode,
        })

    def test_valid_login_both_modes(self):
        for mode in ('vulnerable', 'safe'):
            res = self.post('student', '1234', mode)
            self.assertEqual([u.user_id for u in res.context['results']], ['student'])

    def test_wrong_password_both_modes(self):
        for mode in ('vulnerable', 'safe'):
            res = self.post('student', '1111', mode)
            self.assertEqual(len(res.context['results']), 0)

    def test_injection_bypasses_vulnerable_mode(self):
        res = self.post('student', INJECTION, 'vulnerable')
        self.assertEqual(len(res.context['results']), 3)
        self.assertIn("password = '' or '1' = '1'", res.context['sql_text'])

    def test_injection_blocked_in_safe_mode(self):
        res = self.post('student', INJECTION, 'safe')
        self.assertEqual(len(res.context['results']), 0)
        # 공격 문자열이 SQL이 아닌 바인딩 파라미터(데이터)로 전달됨
        self.assertCountEqual(res.context['params'], ['student', INJECTION])
        self.assertNotIn(INJECTION, res.context['sql_text'])

    def test_comment_injection_in_vulnerable_mode(self):
        # admin' -- : 비밀번호 조건을 주석 처리하여 admin으로 인증 우회
        res = self.post("admin' --", 'anything', 'vulnerable')
        self.assertEqual([u.user_id for u in res.context['results']], ['admin'])

    def test_data_view_lists_seed_users(self):
        res = self.client.get(reverse('data'))
        self.assertEqual(len(res.context['auth_users']), 3)
