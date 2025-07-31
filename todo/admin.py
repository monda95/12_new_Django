from django.contrib import admin
from .models import Todo
from django_summernote.admin import SummernoteModelAdmin


@admin.register(Todo)
class TodoAdmin(SummernoteModelAdmin):
    summernote_fields = ('content')
    list_display = ['title', 'start_date', 'end_date', 'is_completed']
    list_filter = ['is_completed', 'start_date']
    search_fields = ('title',)
    ordering = ('start_date',)
    fieldsets = (
        ('Todo Info', {
            'fields': ('title', 'content', 'image', 'is_completed')
        }),
        ('Date Range', {
            'fields': ('start_date', 'end_date')
        }),
    )