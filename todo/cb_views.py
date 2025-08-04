from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
import json
from collections import defaultdict
import datetime
import calendar
from django.utils import timezone  # 이 줄을 추가합니다.

from todo.models import Todo, Comment
from .forms import TodoForm, CommentForm


class TodoListView(LoginRequiredMixin, ListView):
    model = Todo
    template_name = 'todo_list.html'
    context_object_name = 'todos'

    def get_queryset(self):
        # 현재 로그인한 사용자의 Todo만 가져오도록 필터링
        queryset = super().get_queryset().filter(author=self.request.user).order_by('start_date')

        q = self.request.GET.get('q')

        if q:
            return queryset.filter(
                Q(title__icontains=q) |
                Q(content__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 현재 월과 연도 가져오기 (URL 매개변수 또는 현재 날짜)
        year = int(self.kwargs.get('year', datetime.date.today().year))
        month = int(self.kwargs.get('month', datetime.date.today().month))

        # 달력 생성
        calendar.setfirstweekday(calendar.MONDAY)  # 주 시작 요일을 월요일로 설정
        cal = calendar.Calendar()
        month_calendar = cal.monthdatescalendar(year, month)

        # 해당 월의 모든 Todo 항목 가져오기
        # 달력에 이전/다음 달의 날짜도 포함될 수 있으므로, 해당 범위의 Todo를 모두 가져옴
        first_day_of_month = datetime.date(year, month, 1)
        last_day_of_month = datetime.date(year, month, calendar.monthrange(year, month)[1])

        # 달력에 표시될 가장 빠른 날짜와 가장 늦은 날짜 계산
        start_date = month_calendar[0][0]  # 첫 주의 첫 날
        end_date = month_calendar[-1][-1]  # 마지막 주의 마지막 날

        # 검색어가 있을 경우 검색 결과만 별도로 처리
        q = self.request.GET.get('q')
        if q:
            all_todos_for_search = super().get_queryset().filter(author=self.request.user).filter(
                Q(title__icontains=q) |
                Q(content__icontains=q)
            ).order_by('start_date')
            context['searched_todos'] = all_todos_for_search

        # 달력 데이터 구성은 검색어와 상관없이 전체 Todo 목록을 사용
        todos_in_range = super().get_queryset().filter(author=self.request.user).filter(
            start_date__gte=start_date,
            start_date__lte=end_date
        ).order_by('start_date')

        # 날짜별로 Todo 매핑
        todos_by_date = defaultdict(list)
        for todo in todos_in_range:
            todos_by_date[todo.start_date].append(todo)

        # 달력 데이터 구성
        calendar_weeks = []
        for week in month_calendar:
            week_data = []
            for day in week:
                day_data = {
                    'date': day,
                    'is_current_month': day.month == month,  # 현재 월의 날짜인지 여부
                    'todos': todos_by_date[day],
                    'is_sunday': day.weekday() == calendar.SUNDAY,
                    'is_saturday': day.weekday() == calendar.SATURDAY,
                    'is_today': day == datetime.date.today(),
                }
                week_data.append(day_data)
            calendar_weeks.append(week_data)

        context['calendar_weeks'] = calendar_weeks
        context['current_year'] = year
        context['current_month'] = month
        context['month_name'] = datetime.date(year, month, 1).strftime('%B')  # 월 이름 (예: August)

        # 이전/다음 달 URL
        prev_month_date = datetime.date(year, month, 1) - datetime.timedelta(days=1)
        next_month_date = datetime.date(year, month, 1) + datetime.timedelta(days=32)  # 다음달 1일로 이동

        context['prev_month_url'] = reverse('todo:list_by_month',
                                            kwargs={'year': prev_month_date.year, 'month': prev_month_date.month})
        context['next_month_url'] = reverse('todo:list_by_month',
                                            kwargs={'year': next_month_date.year, 'month': next_month_date.month})

        return context


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

    def get_initial(self):
        initial = super().get_initial()
        date_param = self.request.GET.get('date')
        if date_param:
            try:
                initial['start_date'] = datetime.datetime.strptime(date_param, '%Y-%m-%d').date()
            except ValueError:
                pass  # 유효하지 않은 날짜 형식은 무시
        return initial

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


# 드래그 앤 드롭을 위한 Todo 날짜 업데이트 API
@method_decorator(csrf_exempt, name='dispatch')
class TodoUpdateDateView(LoginRequiredMixin, UpdateView):
    model = Todo
    http_method_names = ['post']
    pk_url_kwarg = 'todo_pk'

    def get_queryset(self):
        # 본인의 Todo만 수정 가능하도록 필터링
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(author=self.request.user)
        return queryset

    def post(self, request, *args, **kwargs):
        try:
            # JSON 데이터 파싱
            data = json.loads(request.body)
            new_date_str = data.get('new_date')

            if not new_date_str:
                return JsonResponse({
                    'success': False,
                    'error': '새 날짜가 제공되지 않았습니다.'
                }, status=400)

            # 날짜 파싱
            try:
                new_date = datetime.datetime.strptime(new_date_str, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': '유효하지 않은 날짜 형식입니다.'
                }, status=400)

            # Todo 객체 가져오기
            todo = self.get_object()

            # 날짜 업데이트
            old_date = todo.start_date
            todo.start_date = new_date
            todo.save(update_fields=['start_date'])

            return JsonResponse({
                'success': True,
                'message': f'할일이 {old_date}에서 {new_date}로 이동되었습니다.',
                'old_date': old_date.strftime('%Y-%m-%d'),
                'new_date': new_date.strftime('%Y-%m-%d')
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'JSON 데이터 파싱 오류입니다.'
            }, status=400)
        except Todo.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '할일을 찾을 수 없습니다.'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'서버 오류: {str(e)}'
            }, status=500)


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