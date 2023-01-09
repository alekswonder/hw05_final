from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from yatube.settings import AMOUNT_OF_POSTS

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post

User = get_user_model()


def get_page_obj(request, queryset, argument):
    paginator = Paginator(queryset, AMOUNT_OF_POSTS)
    page_number = request.GET.get(argument)
    return paginator.get_page(page_number)


def index(request):
    post_list = Post.objects.all()
    context = {
        'page_obj': get_page_obj(request, post_list, 'page'),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author', 'group')
    context = {
        'group': group,
        'page_obj': get_page_obj(request, post_list, 'page'),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('author')
    following = (request.user.is_authenticated
                 and author.following.filter(user=request.user).exists())
    context = {
        'author': author,
        'page_obj': get_page_obj(request, post_list, 'page'),
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = Post.objects.get(pk=post_id)
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post=post)
    context = {
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required(login_url='users:login')
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    form.instance.author = request.user
    if not form.is_valid():
        return render(request, 'posts/post_create.html', {'form': form})
    form.save()
    return redirect('posts:profile', username=request.user.username)


@login_required(login_url='users:login')
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    redirect_to_post_detail = redirect('posts:post_detail', post_id=post_id)

    if not post.author == request.user:
        return redirect_to_post_detail

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if not form.is_valid():
        context = {
            'form': form, 'is_edit': True, 'post_id': post_id
        }
        return render(request, 'posts/post_create.html', context)

    form.save()
    return redirect_to_post_detail


@login_required(login_url='users:login')
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)

    if not form.is_valid():
        return redirect('posts:post_detail', post_id=post_id)

    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required(login_url='users:login')
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    context = {'page_obj': get_page_obj(request, post_list, 'page')}
    return render(request, 'posts/follow.html', context)


@login_required(login_url='users:login')
def profile_follow(request, username):
    redirect_to_profile_page = redirect('posts:profile', username=username)
    if request.user.username == username:
        return redirect_to_profile_page
    following = get_object_or_404(User, username=username)
    is_follow = Follow.objects.filter(
        user=request.user,
        author=following
    ).exists()
    if not is_follow:
        Follow.objects.create(user=request.user, author=following)
    return redirect_to_profile_page


@login_required(login_url='users:login')
def profile_unfollow(request, username):
    following = get_object_or_404(User, username=username)
    follower = get_object_or_404(Follow, author=following, user=request.user)
    follower.delete()
    return redirect('posts:profile', username=username)
