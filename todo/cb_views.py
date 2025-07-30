from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404

from todo.models import Todo, Comment
from .forms import TodoForm, CommentForm


class TodoListView(ListView):
    model = Todo
    queryset = Todo.objects.all().order_by('created_at')
    template_name = 'todo_list.html'
    context_object_name = 'todos'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        q = self.request.GET.get('q')

        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(content__icontains=q)
            )
        return queryset


class TodoDetailView(DetailView):
    model = Todo
    template_name = 'todo_detail.html'
    pk_url_kwarg = 'todo_pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        todo = self.get_object()

        comment_list = todo.comments.all().prefetch_related('author')
        paginator = Paginator(comment_list, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['comments'] = page_obj
        context['page_obj'] = page_obj
        context['comment_form'] = CommentForm()
        context['can_edit'] = (self.request.user == todo.author) or self.request.user.is_superuser
        return context


class TodoCreateView(LoginRequiredMixin, CreateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todo_create.html'
    success_url = reverse_lazy('todo:list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class TodoUpdateView(LoginRequiredMixin, UpdateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todo_update.html'
    pk_url_kwarg = 'todo_pk'

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(author=self.request.user)
        return queryset

    def get_success_url(self):
        return reverse_lazy('todo:detail', kwargs={'todo_pk': self.object.pk})


class TodoDeleteView(LoginRequiredMixin, DeleteView):
    model = Todo
    success_url = reverse_lazy('todo:list')
    pk_url_kwarg = 'todo_pk'

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(author=self.request.user)
        return queryset


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.todo = self.get_todo()
        self.object.save()

        comment_html = render_to_string('partials/_comment.html', {'comment': self.object, 'user': self.request.user})

        return JsonResponse({
            'status': 'success',
            'html': comment_html,
        })

    def form_invalid(self, form):
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    def get_todo(self):
        pk = self.kwargs['todo_pk']
        return get_object_or_404(Todo, pk=pk)


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_pk'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(author=self.request.user)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return JsonResponse({'status': 'success', 'message': 'Comment deleted.'})
