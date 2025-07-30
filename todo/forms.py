from django import forms
from .models import Todo, Comment


class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'content', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control placeholder-center',
                'rows': 4,
                'placeholder': '댓글을 입력하세요...'
            }),
        }
        labels = {
            'content': ''  # 라벨을 비워서 placeholder와 겹치지 않게 함
        }