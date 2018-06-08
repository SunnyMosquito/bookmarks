from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, get_user_model
from django.views.decorators.http import require_POST
from django.conf import settings
from common.decorators import ajax_required
from .models import Profile, Contact
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .authentication import OAuthGithub
from actions.utils import create_action
from actions.models import Action
import uuid

User = get_user_model()

#  Create your views here.
@ajax_required
@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(
                    user_from=request.user,
                    user_to=user
                )
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(
                    user_from=request.user,
                    user_to=user
                ).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return HttpResponse({'stauts': 'ko'})
    return JsonResponse({'status': 'ko'})

def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(request,
                  'account/user/list.html',
                  {'section':'people',
                  'users': users})

def user_detail(request, username):
    user = get_object_or_404(User,
                             username=username,
                             is_active=True)
    return render(request,
                  'account/user/detail.html',
                  {'section': 'people',
                  'user': user}
    )

def github_login(request):
    oauth = OAuthGithub(settings.CLIENT_ID,
                        settings.CLIENT_SECRET, 
                        settings.REDIRECT_URL)
    url = oauth.get_auth_url()
    return HttpResponseRedirect(url)

def callback(request):
    code = request.GET.get('code')
    oauth = OAuthGithub(settings.CLIENT_ID,
                        settings.CLIENT_SECRET, settings.REDIRECT_URL)
    oauth.get_access_token(code)
    user_info = oauth.get_github_info()
    user, created = User.objects.get_or_create(username=user_info['login'])
    # 如果是新增的用户就创建profile，否则就直接获取
    if created:
        pwd = str(uuid.uuid1())  # 随机设置用户密码,可以将密码通过邮件发送给用户
        user.set_password(pwd)
        profile = Profile.objects.create(user=user)
    else:
        profile = user.profile
    # 这里可以对profile进行操作，更改photo之类的
    profile.save()
    user.email = user_info['email']
    # 由于没有执行authenticate()，并且有多个backend，要指定user的backend
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    user.save()
    login(request, user)
    return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)


@login_required
def dashboard(request):
    # 不显示自己的actions
    actions = Action.objects.exclude(user=request.user)
    # flat=true要求每个元素不是元组，而是单个值,没有flat会返回(1,),有就返回1
    following_ids = request.user.following.values_list('id', flat=True)
    if following_ids:
        # If user is following others, retrieve only their actions
        actions = actions.filter(user_id__in=following_ids) \
            .select_related('user', 'user__profile') \
            .prefetch_related('target')
    actions = actions[:10]
    return render(request,
                  'account/dashboard.html',
                  {'section': 'dashboard',
                   'actions':  actions})

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            profile = Profile.objects.create(user=new_user)
            create_action(new_user, 'has created an account')
            return render(request,
                          'account/register_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'account/register.html',
                  {'user_form': user_form})

@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile,
                                       data=request.POST,
                                       files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():  
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile update successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request,
                  'account/edit.html',
                  {'user_form': user_form,
                   'profile_form': profile_form})















def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})
