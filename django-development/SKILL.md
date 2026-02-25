---
name: django-development
description: This skill should be used when building web applications or REST APIs with Django, covering project setup, models and migrations, function-based and class-based views, URL routing, Django REST Framework serializers and viewsets, authentication, middleware, templates, forms, signals, admin customization, and testing.
---
# Django Development
This skill should be used when developing web applications or APIs with Django, spanning project setup, ORM models, views, URL routing, DRF, auth, middleware, templates, forms, signals, admin, and testing.
## Project Setup
```bash
pip install django djangorestframework djangorestframework-simplejwt
django-admin startproject config . && python manage.py startapp core
```
```python
# config/settings.py (key additions)
INSTALLED_APPS += ["rest_framework", "core"]; AUTH_USER_MODEL = "core.User"
REST_FRAMEWORK = {"DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination", "PAGE_SIZE": 20}
```
## Models and Migrations
```python
from django.contrib.auth.models import AbstractUser
from django.db import models; from django.utils.text import slugify
class User(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"; REQUIRED_FIELDS = ["username"]
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
class Article(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft"; PUBLISHED = "published"
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="articles")
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    body = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["-created_at"]
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.title)
        super().save(*args, **kwargs)
# python manage.py makemigrations core && python manage.py migrate
```
## Views (Function-Based and Class-Based)
```python
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView; from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Article; from .forms import ArticleForm
def article_detail(request, slug):  # function-based view
    return render(request, "core/detail.html", {"article": get_object_or_404(Article, slug=slug)})
def article_create_fbv(request):  # function-based view with form handling
    form = ArticleForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False); obj.author = request.user; obj.save(); form.save_m2m()
        return redirect("article-detail", slug=obj.slug)
    return render(request, "core/form.html", {"form": form})
class ArticleListView(ListView):  # class-based view
    queryset = Article.objects.filter(status="published").select_related("author")
    template_name, context_object_name, paginate_by = "core/list.html", "articles", 10
class ArticleCreateView(LoginRequiredMixin, CreateView):  # class-based view with auth
    model, form_class, template_name = Article, ArticleForm, "core/form.html"
    def form_valid(self, form):
        form.instance.author = self.request.user; return super().form_valid(form)
```
## URL Routing
```python
# core/urls.py
from django.urls import path; from . import views
urlpatterns = [path("", views.ArticleListView.as_view(), name="article-list"),
    path("new/", views.ArticleCreateView.as_view(), name="article-create"),
    path("<slug:slug>/", views.article_detail, name="article-detail")]
# config/urls.py
from django.contrib import admin; from django.urls import path, include
urlpatterns = [path("admin/", admin.site.urls), path("articles/", include("core.urls")),
    path("api/", include("core.api_urls")), path("api/auth/", include("core.auth_urls"))]
```
## DRF Serializers and ViewSets
```python
from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import action; from rest_framework.response import Response
from .models import Article, Tag
class ArticleSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, write_only=True, source="tags")
    class Meta:
        model, fields = Article, ["id","title","slug","body","status","author","author_name","tags","tag_ids","created_at"]
        read_only_fields = ["author", "slug"]
    def create(self, vd):
        tags = vd.pop("tags", []); vd["author"] = self.context["request"].user
        article = Article.objects.create(**vd); article.tags.set(tags); return article
class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or obj.author == request.user
class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class, lookup_field = ArticleSerializer, "slug"
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
    def get_queryset(self): return Article.objects.select_related("author").prefetch_related("tags")
    @action(detail=True, methods=["post"])
    def publish(self, request, slug=None):
        article = self.get_object(); article.status = Article.Status.PUBLISHED; article.save(update_fields=["status"])
        return Response(ArticleSerializer(article).data)
# api_urls.py: router=DefaultRouter(); router.register("articles",ArticleViewSet,"article"); urlpatterns=router.urls
```
## Authentication
```python
from datetime import timedelta  # Add to settings.py
SIMPLE_JWT = {"ACCESS_TOKEN_LIFETIME": timedelta(minutes=30), "ROTATE_REFRESH_TOKENS": True}
# auth_urls.py
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns = [path("token/",TokenObtainPairView.as_view()), path("token/refresh/",TokenRefreshView.as_view())]
```
## Middleware
```python
import time, logging; logger = logging.getLogger(__name__)
class RequestTimingMiddleware:  # Add "core.middleware.RequestTimingMiddleware" to MIDDLEWARE
    def __init__(self, get_response): self.get_response = get_response
    def __call__(self, request):
        start = time.monotonic(); response = self.get_response(request)
        dur = time.monotonic() - start; response["X-Request-Duration"] = f"{dur:.3f}s"
        if dur > 1.0: logger.warning("Slow: %s %s %.3fs", request.method, request.path, dur)
        return response
```
## Templates
```html
{% extends "base.html" %}
{% block content %}<h1>Articles</h1>
{% for a in articles %}
  <h2><a href="{% url 'article-detail' a.slug %}">{{ a.title }}</a></h2>
  <p>{{ a.author.username }} | {{ a.created_at|date:"M d, Y" }}</p>
  <p>{{ a.body|truncatewords:30 }}</p>
{% empty %}<p>No articles.</p>{% endfor %}{% endblock %}
```
## Forms
```python
from django import forms; from .models import Article
class ArticleForm(forms.ModelForm):
    class Meta:
        model, fields = Article, ["title", "body", "status", "tags"]
        widgets = {"body": forms.Textarea(attrs={"rows": 8}), "tags": forms.CheckboxSelectMultiple}
    def clean_title(self):
        title = self.cleaned_data["title"]
        if len(title) < 5: raise forms.ValidationError("Title must be at least 5 characters.")
        return title
```
## Signals
```python
from django.db.models.signals import post_save; from django.dispatch import receiver; from .models import Article
@receiver(post_save, sender=Article)
def on_article_published(sender, instance, **kwargs):
    if instance.status == Article.Status.PUBLISHED:
        pass  # notify, clear cache, reindex
# Register in apps.py CoreConfig.ready(): import core.signals
```
## Admin Customization
```python
from django.contrib import admin; from .models import Article, Tag
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "status", "created_at"]
    list_filter, search_fields = ["status", "created_at", "tags"], ["title", "body"]
    prepopulated_fields, raw_id_fields = {"slug": ("title",)}, ["author"]
    date_hierarchy, actions = "created_at", ["make_published"]
    @admin.action(description="Publish selected")
    def make_published(self, request, qs): qs.update(status="published")
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display, search_fields = ["name"], ["name"]
```
## Testing
```python
from django.test import TestCase
from rest_framework.test import APIClient; from rest_framework import status as s
from .models import User, Article
class ArticleAPITest(TestCase):
    def setUp(self):
        self.c = APIClient()
        self.user = User.objects.create_user(username="u", email="u@t.com", password="pass1234")
        self.c.force_authenticate(self.user)
        self.art = Article.objects.create(author=self.user, title="Test", body="x", status="published")
    def test_list(self):
        self.assertEqual(self.c.get("/api/articles/").status_code, s.HTTP_200_OK)
    def test_create(self):
        r = self.c.post("/api/articles/", {"title":"New","body":"y","tag_ids":[]}, format="json")
        self.assertEqual(r.status_code, s.HTTP_201_CREATED)
    def test_unauthorized_edit(self):
        other = User.objects.create_user(username="o", email="o@t.com", password="pass1234")
        self.c.force_authenticate(other)
        self.assertEqual(self.c.patch(f"/api/articles/{self.art.slug}/",
            {"title":"X"}, format="json").status_code, s.HTTP_403_FORBIDDEN)
    def test_publish(self):
        d = Article.objects.create(author=self.user, title="Draft", body="b")
        self.c.post(f"/api/articles/{d.slug}/publish/"); d.refresh_from_db()
        self.assertEqual(d.status, "published")
```
## Additional Resources
- Django documentation: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- djangorestframework-simplejwt: https://django-rest-framework-simplejwt.readthedocs.io/
- Django Testing: https://docs.djangoproject.com/en/stable/topics/testing/
- Two Scoops of Django: https://www.feldroy.com/books/two-scoops-of-django-5-0
