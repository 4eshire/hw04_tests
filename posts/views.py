from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    post_list = Post.objects.select_related('group')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "index.html", {
        'page': page, "paginator": paginator, })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
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
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "profile.html", {
        "author": author,
        "page": page,
        "paginator": paginator
    })


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    return render(request, "post.html", {
        "author": author,
        "post": post,
    })

@login_required
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    if request.user.username != author.username:
        return redirect('post', username, post_id)
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(instance=post)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('post', username, post_id)
    return render(request, "new_post.html",
                  {"author": author, "form": form,
                   'post': post})


def page_not_found(request, exception=None):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
