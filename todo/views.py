from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from todo.models import Todo

def todo_list(request):
#     return HttpResponse('<h1>Todo list 페이지입니다.</h1>')
    todo = Todo.objects.all()

    context = {
        'todo': todo,
    }
    return render(request, 'todolist.html', context)


def todo_detail(request, pk):
    # try:
    #     bookmark = Bookmark.objects.get(pk=pk)
    # except:
    #     raise Http404
    todo = get_object_or_404(Todo, pk=pk)
    context = {'todo': todo}
    return render(request, 'tododetail.html', context)