---
name: python-django
description: Python Django patterns covering models, views, serializers, Django REST Framework, authentication, middleware, signals, admin customization, and testing.
---

# Python Django

This skill should be used when building web applications with Python Django. It covers models, views, DRF serializers, authentication, middleware, signals, and testing.

## When to Use This Skill

Use this skill when you need to:

- Build web applications with Django ORM and views
- Create REST APIs with Django REST Framework
- Implement authentication and permissions
- Customize the Django admin
- Write Django tests

## Setup

```bash
pip install django djangorestframework
django-admin startproject myproject
cd myproject
python manage.py startapp users
```

## Models

```python
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=200)
    body = models.TextField()
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
```

## DRF Serializers

```python
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "bio", "created_at"]
        read_only_fields = ["id", "created_at"]

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ["id", "author", "title", "body", "published", "created_at"]

class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["title", "body", "published"]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)
```

## ViewSets

```python
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("author")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "body"]
    ordering_fields = ["created_at", "title"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return CreatePostSerializer
        return PostSerializer

    @action(detail=False, methods=["get"])
    def published(self, request):
        posts = self.queryset.filter(published=True)
        page = self.paginate_queryset(posts)
        serializer = PostSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
```

## URLs

```python
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("posts", PostViewSet)
router.register("users", UserViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]
```

## Custom Permissions

```python
from rest_framework.permissions import BasePermission

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
```

## Middleware

```python
import time

class TimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration = time.time() - start
        response["X-Response-Time"] = f"{duration:.3f}s"
        return response
```

## Testing

```python
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse

class PostTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_post(self):
        url = reverse("post-list")
        data = {"title": "Test Post", "body": "Content"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Post.objects.count(), 1)

    def test_list_posts(self):
        Post.objects.create(author=self.user, title="Post 1", body="Body")
        url = reverse("post-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
```

## Additional Resources

- Django: https://docs.djangoproject.com/
- DRF: https://www.django-rest-framework.org/
- Django Tutorial: https://docs.djangoproject.com/en/stable/intro/tutorial01/
