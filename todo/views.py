from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404

from todo.models import Todo
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from todo.forms import TodoForm
from django.core.paginator import Paginator

import datetime
import calendar


@login_required()
def todo_list(request):
    todos = Todo.objects.all().order_by('created_at')

    q = request.GET.get('q')
    if q:
        todos = todos.filter(Q(title__icontains=q) |
                             Q(content__icontains=q)
        )
    
    # 캘린더 관련 로직 추가
    today = datetime.date.today()
    current_year = int(request.GET.get('year', today.year))
    current_month = int(request.GET.get('month', today.month))

    cal = calendar.Calendar()
    month_days = cal.monthdayscalendar(current_year, current_month)

    calendar_weeks = []
    for week in month_days:
        week_data = []
        for day in week:
            day_date = None
            is_current_month = True
            is_today = False
            day_todos = []

            if day != 0:
                day_date = datetime.date(current_year, current_month, day)
                if day_date == today:
                    is_today = True
                
                # 해당 날짜의 Todo 가져오기
                day_todos = Todo.objects.filter(
                    author=request.user,
                    start_date__lte=day_date,
                    end_date__gte=day_date
                ).order_by('start_date')

            else: # 다른 달의 날짜
                is_current_month = False
                # 다른 달의 날짜는 표시하지 않거나, 필요에 따라 처리

            week_data.append({
                'date': day_date,
                'is_current_month': is_current_month,
                'is_today': is_today,
                'is_saturday': day_date and day_date.weekday() == 5, # 토요일 (5)
                'is_sunday': day_date and day_date.weekday() == 6,   # 일요일 (6)
                'todos': day_todos,
            })
        calendar_weeks.append(week_data)

    # 이전 달, 다음 달 URL 생성
    prev_month_date = datetime.date(current_year, current_month, 1) - datetime.timedelta(days=1)
    next_month_date = datetime.date(current_year, current_month, 1) + datetime.timedelta(days=32) # 다음 달로 넘어가기 위해 넉넉하게 32일 더함

    prev_month_url = reverse('todo:list') + f'?year={prev_month_date.year}&month={prev_month_date.month}'
    next_month_url = reverse('todo:list') + f'?year={next_month_date.year}&month={next_month_date.month}'


    paginator = Paginator(todos, 10)
    page = request.GET.get('page')
    page_object = paginator.get_page(page)

    if paginator.num_pages <= 1:  # 게시글이 10개 이하이면 페이지가 1개 이하로 나올 것
        show_pages = [1]  # 첫 페이지만 보여줌
    else:
        # 일반적인 페이지네이션 처리
        show_pages = paginator.page_range

    context = {
        'todos': todos,
        'page_object': page_object,
        'show_pages': show_pages,
        'current_year': current_year,
        'current_month': current_month,
        'calendar_weeks': calendar_weeks,
        'prev_month_url': prev_month_url,
        'next_month_url': next_month_url,
    }
    return render(request, 'todo_list.html', context)


def todo_detail(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    is_author = False
    if request.user.is_authenticated and request.user == todo.author:
        is_author = True
    context = {'todo': todo, 'is_author': is_author}
    return render(request, 'todo_detail.html', context)


@login_required()
def todo_create(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.author = request.user
            todo.save()

            return redirect(reverse('todo:detail', kwargs={'pk': todo.pk}))  # 'blog_detail' -> 'todo_detail'
    else:
        form = TodoForm()
    context = {'form': form}
    return render(request, 'todo_create.html', context)  # 'blog_create' -> 'todo_create'


@login_required()
def todo_update(request, pk):  # 'blog_update' -> 'todo_update'
    todo = get_object_or_404(Todo, pk=pk, author=request.user)

    form = TodoForm(request.POST or None, instance=todo)
    if form.is_valid():
        todo = form.save()
        return redirect(reverse('todo:detail', kwargs={'pk': todo.pk}))  # 'blog_detail' -> 'todo_detail'

    context = {
        'todo': todo,
        'form': form
    }
    return render(request, 'todo_update.html', context)  # 'blog_update' -> 'todo_update'


@login_required()
@require_http_methods(['POST'])
def todo_delete(request, pk):
    todo = get_object_or_404(Todo, pk=pk, author=request.user)
    todo.delete()

    return redirect(reverse('todo:list'))
