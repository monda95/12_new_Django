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


def todo_list(request):
    todos = Todo.objects.all().order_by('created_at')

    q = request.GET.get('q')
    if q:
        todos = todos.filter(Q(title__icontains=q) |
                             Q(content__icontains=q)
        )
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