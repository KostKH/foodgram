from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Subscriptions, User
from .serializers import SubscribeSerializer, SubscriptionsSerializer


class SubsriptionsView(ListAPIView):

    serializer_class = SubscriptionsSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return user.followed_authors.all().order_by('-id')


class SubscribeView(APIView):
    pagination_class = None
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, id):
        author = get_object_or_404(User, id=id)
        user = self.request.user
        data = {'user': user.id, 'author': author.id}
        serializer = SubscribeSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        author = get_object_or_404(User, id=id)
        user = self.request.user
        subscription = get_object_or_404(
            Subscriptions, user=user, author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
