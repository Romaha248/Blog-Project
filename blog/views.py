from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.views import View
from django.urls import reverse

from .models import Post
from .forms import CommentForm

# Create your views here.


class IndexView(ListView):
    template_name = "blog/index.html"
    model = Post
    ordering = ["-date"]
    context_object_name = "posts"

    def get_queryset(self):
        queryset = super().get_queryset()
        data = queryset[:3]
        return data


# def index(request):
#     posts = Post.objects.all().order_by("-date")[:3]
#     return render(request, "blog/index.html", {
#         "posts": posts
#     })


class AllPostsView(ListView):
    template_name = "blog/posts.html"
    model = Post
    context_object_name = "posts"
    ordering = ["-date"]


# def all_posts(request):
#     posts = Post.objects.all().order_by("-date")
#     return render(request, "blog/posts.html", {
#         "posts": posts
#     })


class PostDetailView(View):
    template_name = "blog/post.html"
    # model = Post
    # context_object_name = "post"

    def is_stored_for_later(self, request, post_id):
        stored_posts = request.session.get("stored_posts")
        if stored_posts is not None:
            return post_id in stored_posts
        return False

    def get(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        context = {
            "post": post,
            "tags": post.tag.all(),
            "comment_form": CommentForm(),
            "comments": post.comments.all().order_by("-id"),
            "saved_for_later": self.is_stored_for_later(request, post.id),
        }
        return render(request, self.template_name, context)

    def post(self, request, slug):
        comment_form = CommentForm(request.POST)
        post = get_object_or_404(Post, slug=slug)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = get_object_or_404(Post, slug=slug)
            comment.save()
            return redirect("post", slug=slug)

        context = {
            "post": post,
            "tags": post.tag.all(),
            "comment_form": comment_form,
            "comments": post.comments.all().order_by("-id"),
            "saved_for_later": self.is_stored_for_later(request, post.id),
        }
        return render(request, self.template_name, context)
        # return redirect(reverse("post", kwargs={"slug": slug}))

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["tags"] = self.object.tag.all()
    #     context["comment_form"] = CommentForm()
    #     return context
    # return redirect("post", slug=slug# def post(request, slug):


#     post = get_object_or_404(Post, slug=slug)
#     return render(request, "blog/post.html", {
#         "post": post,
#         "tags": post.tag.all()
#     })


class ReadLaterView(View):

    def get(self, request):
        stored_posts = request.session.get("stored_posts")

        context = {}

        if stored_posts is None or len(stored_posts) == 0:
            context["posts"] = []
            context["has_posts"] = False
        else:
            posts = Post.objects.filter(id__in=stored_posts)
            context["posts"] = posts
            context["has_posts"] = True

        return render(request, "blog/stored_post.html", context)

    def post(self, request):
        stored_posts = request.session.get("stored_posts")

        if stored_posts is None:
            stored_posts = []

        post_id = int(request.POST["post_id"])

        if post_id not in stored_posts:
            stored_posts.append(post_id)
        else:
            stored_posts.remove(post_id)

        request.session["stored_posts"] = stored_posts

        return redirect("/")
