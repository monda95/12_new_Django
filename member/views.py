from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import FormView, View, RedirectView
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login, logout
from django.core import signing
from django.core.signing import SignatureExpired, TimestampSigner
from django.contrib.messages.views import SuccessMessageMixin  # 추가
from django.contrib import messages  # 추가
from django.http import JsonResponse

from .forms import SignupForm, LoginForm, ProfileForm
from .models import User
from utils.email import send_email


class IndexView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse_lazy('todo:list'))
        return render(request, 'home.html')


class SignupView(FormView):
    template_name = 'auth/signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('signup_done')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False  # 이메일 인증 전까지 비활성화
        user.save()

        # 이메일 발송
        signer = TimestampSigner()
        signed_user_email = signer.sign(user.email)

        url = self.request.build_absolute_uri(
            reverse('verify_email') + f'?code={signed_user_email}'
        )

        subject = '[Todolist] 이메일 인증을 완료해주세요'
        message = f'다음 링크를 클릭하여 이메일 인증을 완료해주세요: <a href="{url}">{url}</a>'
        send_email(subject, message, [user.email])

        return super().form_valid(form)


class SignupDoneView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'auth/signup_done.html')


class VerifyEmailView(View):
    def get(self, request, *args, **kwargs):
        code = request.GET.get('code', '')
        signer = TimestampSigner()

        try:
            email = signer.unsign(code, max_age=1800)  # 30분 유효
        except SignatureExpired:
            return render(request, 'auth/not_verified.html', {'message': '인증 링크가 만료되었습니다.'})
        except signing.BadSignature:
            return render(request, 'auth/not_verified.html', {'message': '잘못된 인증 링크입니다.'})

        user = get_object_or_404(User, email=email, is_active=False)
        user.is_active = True
        user.save()

        login(request, user)
        return render(request, 'auth/email_verified_done.html')


class LoginView(FormView):
    template_name = 'auth/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('todo:list')

    def form_valid(self, form):
        user = form.get_user()
        if user is not None and user.is_active:
            login(self.request, user)
            return super().form_valid(form)
        else:
            # 비활성화된 사용자 또는 유효하지 않은 사용자 처리
            form.add_error(None, "이메일 인증이 필요하거나, 유효하지 않은 사용자입니다.")
            return self.form_invalid(form)


class LogoutView(RedirectView):
    url = reverse_lazy('member:login')  # 로그아웃 후 리다이렉트할 URL

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'auth/profile_update.html'

    def get_object(self, queryset=None):
        return self.request.user  # 현재 로그인한 사용자 객체를 가져옴

    def form_valid(self, form):
        # 이전 페이지 URL 저장
        referer_url = self.request.META.get('HTTP_REFERER', reverse_lazy('todo:list'))

        # 폼 저장
        self.object = form.save()

        # AJAX 요청인 경우 JSON 응답
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': '닉네임이 성공적으로 등록되었습니다!',
                'redirect_url': referer_url
            })

        # 일반 요청인 경우 메시지와 함께 리다이렉트
        messages.success(self.request, '닉네임이 성공적으로 등록되었습니다!')
        return redirect(referer_url)

    def form_invalid(self, form):
        # AJAX 요청인 경우 JSON 응답
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = error_list

            return JsonResponse({
                'success': False,
                'errors': errors
            }, status=400)

        # 일반 요청인 경우 기본 처리
        return super().form_invalid(form)