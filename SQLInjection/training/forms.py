from django import forms


class LoginForm(forms.Form):
    MODE_CHOICES = [
        ('vulnerable', '취약코드검색'),
        ('safe', '안전코드검색'),
    ]

    user_id = forms.CharField(label='ID', max_length=100)
    # 공격 문자열을 눈으로 확인할 수 있도록 PasswordInput 대신 TextInput 사용
    password = forms.CharField(label='Password', max_length=100)
    # 값은 두 개의 submit 버튼(name="mode")에서 전달된다
    mode = forms.ChoiceField(choices=MODE_CHOICES, required=False)
