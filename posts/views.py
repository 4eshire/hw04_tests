from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    post_list = Post.objects.select_related('group').order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "index.html", {
        'page': page, "paginator": paginator, })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.select_related('group').filter(group__slug=slug).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {
        "group": group, "page": page, "paginator": paginator, })


class NewPost(LoginRequiredMixin, CreateView):
    login_url = "signup"
    redirect_field_name = 'new_post'
    form_class = PostForm
    success_url = reverse_lazy("index")
    template_name = "new_post.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    post_list = user_profile.posts.all().order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "profile.html",
                  {"user_profile": user_profile,
                   "page": page, "post_list": post_list,
                   "paginator": paginator})


def post_view(request, username, post_id):
    user_profile = get_object_or_404(User, username=username)
    post_list = user_profile.posts.all().order_by('-pub_date')
    post = post_list.get(id=post_id)
    paginator = Paginator(post_list.filter(id=post_id), 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "post.html",
                  {"user_profile": user_profile,
                   "page": page, "post_list": post_list, "post": post, })

@login_required
def post_edit(request, username, post_id):
    user_profile = get_object_or_404(User, username=username)
    if request.user.username != user_profile.username:
        return redirect('post', username, post_id)
    post_list = user_profile.posts.all()
    post = post_list.get(id=post_id)
    form = PostForm(instance=post)
    if request.user.username == user_profile.username:
        if request.method == 'POST':
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                form.save()
                return redirect('post', username, post_id)
        return render(request, "new_post.html",
                  {"user_profile": user_profile, "form": form, })
