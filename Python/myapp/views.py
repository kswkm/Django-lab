from django.shortcuts import render, redirect
from .forms import ScoreForm
from .models import Score1

def index(request):
    if request.method == 'POST':          # [저장] 클릭 시
        form = ScoreForm(request.POST)
        if form.is_valid():
            Score1.objects.create(
                myname1=form.cleaned_data['myname1'],
                score1=form.cleaned_data['score1'],
            )
            return redirect('success')
    else:
        form = ScoreForm()                 # 처음 접속 시 빈 폼
    return render(request, 'index.html', {'form': form})

def success(request):
    all_scores = Score1.objects.all()
    return render(request, 'success.html', {'all_scores': all_scores})