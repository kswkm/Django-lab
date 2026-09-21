from django import forms

class ScoreForm(forms.Form):
    myname1 = forms.CharField(max_length=100)
    score1 = forms.IntegerField()

