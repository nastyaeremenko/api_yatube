import django_filters.rest_framework
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)

from .models import Post, Follow, Group
from .permissions import IsAuthorOrReadOnly
from .serializers import (PostSerializer, CommentSerializer,
                          FollowSerializer, GroupSerializer)

PERMISSION_CLASSES = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
User = get_user_model()


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = PERMISSION_CLASSES
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['group', ]

    def perform_create(self, serializer, *args, **kwargs):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = PERMISSION_CLASSES

    def get_queryset(self):
        post_id = self.kwargs.get('post_id', '')
        post = get_object_or_404(Post, pk=post_id)
        all_comments_of_post = post.comments.all()
        return all_comments_of_post

    def perform_create(self, serializer, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id', ''))
        save_params = {
            'author': self.request.user,
            'post': post
        }
        serializer.save(**save_params)


class FollowViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['=user__username', '=following__username']

    def get_queryset(self):
        following = self.request.user
        return Follow.objects.filter(following=following)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
