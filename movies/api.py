from django.shortcuts import get_object_or_404
from rest_framework import viewsets, renderers, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Actor
from .serializers import (
    ActorListSerializer,
    ActorDetailSerializer
)

"""viewset - позволяет описывать методы и к этоим методом http  хапросы с клиентской стороны """
class ActorViewSet(viewsets.ViewSet):
    """ViewSet - это базовый класс, и вот что внутри ReadOnly.. and ModelViewSet"""

    def list(self, request):
        """list - говорит что мы буем выводить некий список и в нем описавать их,
         а в урл указать этот метод отноясящийся к http запросу"""
        queryset = Actor.objects.all()
        serializer = ActorListSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """retrieve будет принимать рк полученный с урл"""
        queryset = Actor.objects.all()
        actor = get_object_or_404(queryset, pk=pk)
        serializer = ActorDetailSerializer(actor)
        return Response(serializer.data)

