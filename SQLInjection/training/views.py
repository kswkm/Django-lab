from django.db import connection
from django.shortcuts import render

from .forms import LoginForm
from .models import Auth

# [취약] 외부 입력값을 문자열 결합(format)으로 SQL에 직접 이어 붙인다.
VULNERABLE_LOGIN_SQL = (
    "SELECT * FROM training_auth "
    "WHERE user_id = '{user_id}' AND password = '{password}'"
)


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            password = form.cleaned_data['password']
            mode = form.cleaned_data['mode'] or 'safe'

            if mode == 'vulnerable':
                # 입력값이 SQL 구문의 일부로 해석된다 → SQL Injection 가능
                sql_text = VULNERABLE_LOGIN_SQL.format(user_id=user_id, password=password)
                with connection.cursor() as cursor:
                    cursor.execute(sql_text)
                    rows = cursor.fetchall()
                result_ids = [row[0] for row in rows]
                results = Auth.objects.filter(pk__in=result_ids).order_by('pk')
                params = None
                title = '취약코드검색 결과'
            else:
                # ORM이 %s 매개변수(Placeholder)로 쿼리를 만들고 입력값은 바인딩 단계에서 데이터로만 치환
                results = Auth.objects.filter(user_id=user_id, password=password)
                sql_text, params = results.query.sql_with_params()
                params = list(params)
                title = '안전코드검색 결과'

            return render(request, 'training/result.html', {
                'title': title,
                'mode': mode,
                'sql_text': sql_text,
                'params': params,
                'results': results,
            })
    else:
        mode = request.GET.get('mode', 'vulnerable')
        form = LoginForm(initial={'mode': mode})

    return render(request, 'training/login.html', {'form': form})


def data_view(request):
    auth_users = Auth.objects.all().order_by('pk')
    return render(request, 'training/data.html', {'auth_users': auth_users})
