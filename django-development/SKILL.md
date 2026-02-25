---
name: django-development
description: Django web development covering project structure, models, views, templates, Django REST Framework, authentication, middleware, signals, Celery task queues, database optimization, testing, and production deployment patterns with Python.
---

# Django Development

This skill should be used when building web applications or APIs with Django. It covers project structure, ORM models, views, Django REST Framework, authentication, background tasks with Celery, and production deployment patterns.

## When to Use This Skill

Use this skill when you need to:

- Build web applications or REST APIs with Django
- Design database models with Django ORM
- Implement authentication and permissions
- Build APIs with Django REST Framework
- Handle background tasks with Celery
- Optimize database queries
- Test Django applications
- Deploy Django to production

## Project Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Unix
venv\Scripts\activate     # Windows

# Install Django
pip install django djangorestframework django-cors-headers
pip install psycopg[binary] django-environ celery[redis]

# Create project
django-admin startproject config .
python manage.py startapp users
python manage.py startapp posts
```

### Project Structure

```
project/
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py
├── apps/
│   ├── users/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── signals.py
│   │   └── tests/
│   └── posts/
├── manage.py
└── requirements.txt
```

### Settings

```python
# config/settings/base.py
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "corsheaders",
    "django_filters",
    # Local
    "apps.users",
    "apps.posts",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

DATABASES = {
    "default": env.db("DATABASE_URL", default="sqlite:///db.sqlite3"),
}

AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}
```

## Models

```python
# apps/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.email


# apps/posts/models.py
from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    content = models.TextField()
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.DRAFT
    )
    tags = models.ManyToManyField("Tag", blank=True, related_name="posts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["status", "-created_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name
```

## Serializers

```python
# apps/posts/serializers.py
from rest_framework import serializers
from .models import Post, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]


class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        write_only=True,
        source="tags",
    )

    class Meta:
        model = Post
        fields = [
            "id", "title", "slug", "content", "status",
            "author", "author_name", "tags", "tag_ids",
            "created_at", "updated_at",
        ]
        read_only_fields = ["author", "slug"]

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        validated_data["author"] = self.context["request"].user
        post = Post.objects.create(**validated_data)
        post.tags.set(tags)
        return post
```

## Views

```python
# apps/posts/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Post
from .serializers import PostSerializer


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
    filterset_fields = ["status", "author"]
    search_fields = ["title", "content"]
    ordering_fields = ["created_at", "title"]

    def get_queryset(self):
        qs = Post.objects.select_related("author").prefetch_related("tags")
        if self.action == "list":
            if not self.request.user.is_staff:
                qs = qs.filter(status=Post.Status.PUBLISHED) | qs.filter(
                    author=self.request.user
                )
        return qs

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        post = self.get_object()
        post.status = Post.Status.PUBLISHED
        post.save(update_fields=["status", "updated_at"])
        return Response(PostSerializer(post).data)
```

### URL Configuration

```python
# apps/posts/urls.py
from rest_framework.routers import DefaultRouter
from .views import PostViewSet

router = DefaultRouter()
router.register("posts", PostViewSet, basename="post")
urlpatterns = router.urls

# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.posts.urls")),
    path("api/v1/auth/", include("apps.users.urls")),
]
```

## Authentication with JWT

```python
# pip install djangorestframework-simplejwt
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
}

# apps/users/urls.py
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import RegisterView, ProfileView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
```

## Signals

```python
# apps/users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Send welcome email, create related objects, etc.
        from apps.notifications.tasks import send_welcome_email
        send_welcome_email.delay(instance.id)
```

## Celery Background Tasks

```python
# config/celery.py
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# config/settings/base.py
CELERY_BROKER_URL = env("REDIS_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# apps/posts/tasks.py
from celery import shared_task
from django.core.mail import send_mail


@shared_task(bind=True, max_retries=3)
def notify_subscribers(self, post_id):
    try:
        from .models import Post
        post = Post.objects.select_related("author").get(id=post_id)
        subscribers = post.author.followers.values_list("email", flat=True)
        send_mail(
            subject=f"New post: {post.title}",
            message=f"{post.author.username} published a new post.",
            from_email="noreply@example.com",
            recipient_list=list(subscribers),
        )
    except Exception as exc:
        self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
```

## Query Optimization

```python
# Avoid N+1 queries
# Bad: N+1
posts = Post.objects.all()
for post in posts:
    print(post.author.username)  # Hits DB for each post

# Good: select_related for ForeignKey/OneToOne
posts = Post.objects.select_related("author").all()

# Good: prefetch_related for ManyToMany/reverse FK
posts = Post.objects.prefetch_related("tags", "comments").all()

# Conditional prefetch
from django.db.models import Prefetch
posts = Post.objects.prefetch_related(
    Prefetch(
        "comments",
        queryset=Comment.objects.filter(is_approved=True).select_related("user"),
        to_attr="approved_comments",
    )
)

# Aggregation
from django.db.models import Count, Avg, Q
stats = Post.objects.aggregate(
    total=Count("id"),
    published=Count("id", filter=Q(status="published")),
    avg_comments=Avg("comments_count"),
)

# Bulk operations
Post.objects.bulk_create([Post(title=f"Post {i}", author=user) for i in range(100)])
Post.objects.filter(status="draft").update(status="archived")

# Only fetch needed fields
Post.objects.values_list("id", "title", flat=False)
Post.objects.only("id", "title", "slug")
Post.objects.defer("content")  # Exclude heavy fields
```

## Custom Middleware

```python
# apps/core/middleware.py
import time
import logging

logger = logging.getLogger(__name__)


class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        response = self.get_response(request)
        duration = time.monotonic() - start
        response["X-Request-Duration"] = f"{duration:.3f}s"
        if duration > 1.0:
            logger.warning(f"Slow request: {request.method} {request.path} ({duration:.3f}s)")
        return response
```

## Testing

```python
# apps/posts/tests/test_views.py
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User
from apps.posts.models import Post


class PostAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.post = Post.objects.create(
            author=self.user,
            title="Test Post",
            content="Test content",
            status=Post.Status.PUBLISHED,
        )

    def test_list_posts(self):
        response = self.client.get("/api/v1/posts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_post(self):
        data = {"title": "New Post", "content": "Content", "tag_ids": []}
        response = self.client.post("/api/v1/posts/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)

    def test_unauthorized_update(self):
        other_user = User.objects.create_user(
            username="other", email="other@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=other_user)
        response = self.client.patch(
            f"/api/v1/posts/{self.post.id}/",
            {"title": "Hacked"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# pytest with factory_boy
# pip install pytest-django factory-boy
import factory

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")

class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post
    author = factory.SubFactory(UserFactory)
    title = factory.Faker("sentence")
    content = factory.Faker("paragraph")
```

## Production Deployment

```python
# config/settings/production.py
from .base import *

DEBUG = False
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Static files with whitenoise
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "WARNING"},
    },
}
```

```dockerfile
# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

## Additional Resources

- Django docs: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- Celery: https://docs.celeryq.dev/
- django-environ: https://django-environ.readthedocs.io/
- pytest-django: https://pytest-django.readthedocs.io/
