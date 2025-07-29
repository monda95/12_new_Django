from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from todo.models import Todo
from .forms import TodoForm


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_edit'] = (self.request.user == self.object.author) or self.request.user.is_superuser
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

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(author=self.request.user)
        return queryset

    def get_success_url(self):
        return reverse_lazy('todo:detail', kwargs={'pk': self.object.pk})


class TodoDeleteView(LoginRequiredMixin, DeleteView):
    model = Todo
    success_url = reverse_lazy('todo:list')

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(author=self.request.user)
        return queryset
