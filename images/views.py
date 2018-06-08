from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ImageCreateForm
from .models import Image
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.http.response import JsonResponse
from common.decorators import ajax_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from actions.utils import create_action
import redis
from django.conf import settings

r = redis.StrictRedis(host=settings.REDIS_HOST,
                      port=settings.REDIS_PORT,
                      db=settings.REDIS_DB)

# Create your views here.

@login_required
def image_list(request):
    images = Image.objects.all().order_by('id')
    # 显示8张图片
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        images = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            # If the request is AJAX and the page is out of range return an empty page
            return HttpResponse('')
        # If page is out of range deliver last page of results
        images = paginator.page(paginator.num_pages)
    # ajax请求就返回list_ajax部分页面，由jquery添加到图片列表
    if request.is_ajax():
        return render(request,
                      'images/image/list_ajax.html',
                      {'section': 'images', 'images': images})
    return render(request,
                  'images/image/list.html',
                  {'section': 'images', 'images': images})

@login_required
def image_create(request):
    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            # cd = form.cleaned_data
            new_item = form.save(commit=False)
            new_item.user = request.user
            new_item.save()
            create_action(request.user, 'bookmarked image', new_item)
            messages.success(request, 'Image added successfully')
            return redirect(new_item.get_absolute_url())
    
    else:
        form = ImageCreateForm(data=request.GET)
    
    return render(request, 'images/image/create.html',{'section': 'images','form': form})


@login_required
def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    total_views = r.incr('image:{}:views'.format(image.id))
    # zincrby key  member increment
    # 为有序集 key 的成员 member 的 score 值加上增量 increment
    r.zincrby('image_ranking', image.id, 1)
    return render(request, 
                  'images/image/detail.html', 
                  {'section':'images', 
                  'image': image,
                  'total_views': total_views})

@login_required
def image_ranking(request):
    # 反序，由大到小排列
    image_ranking = r.zrange('image_ranking', 0, -1, desc=True)[:10]
    print(image_ranking)
    image_ranking_ids = [int(id) for id in image_ranking]
    most_viewed = list(Image.objects.filter(
                       id__in=image_ranking_ids))
    # 排序这些Image对象通过它们在图片排行中的索引
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    return render(request,
                  'images/image/ranking.html',
                  {'section': 'images',
                  'most_viewed': most_viewed})

@ajax_required
@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except:
            pass
    return JsonResponse({'status': 'ko'})
