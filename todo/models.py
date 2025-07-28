from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Todo(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_completed = models.BooleanField(default=False)

    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = '할 일'
        verbose_name_plural = '할 일 목록'
