from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Movie
from .serializers import *


class MovieListView(APIView):
    """вывод списка фильмов"""
    def get(self, request):
        movies = Movie.objects.filter(draft=False)
        # в переменную сериалайзер мы будем заносить работу нашего сириализатора
        serializer = MovieListSerializer(movies, many=True)  # movies - передаем туда наш  queryset, many=True - гвоорит о том что у нас будет несколько записей
        return Response(serializer.data)


class MovieDetailView(APIView):
    """вывод полного филмьа  """

    def get(self, request, pk):
        # из бд забирает обьект
        movie = Movie.objects.get(id=pk, draft=False)
        # в переменную сериалайзер мы будем заносить работу нашего сириализатора
        serializer = MovieDetailSerializer(movie)  # movies - передаем туда наш  queryset, many=True - гвоорит о том что у нас будет несколько записей
        return Response(serializer.data)


class ReviewCreateView(APIView):
    """вывод полного филмьа  """

    def post(self, request):
        review = ReviewCreateSerializer(data=request.data)  # передаем наши поля с клиентского запроса request.data
        if review.is_valid():
            review.save()
        return Response(status=201)

    # {
    # "email": "test@gmail.com",
    # "name": "Mike",
    # "text": "some text",
    # "movie": 2
    # }


class AddStarRatingView(APIView):
    """Добавление рейтинга фильму"""

    def get_client_ip(self, request):
        """определяем айпи нашего юзера"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def post(self, request):
        serializer = CreateRatingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ip=self.get_client_ip(request))
            return Response(status=201)
        else:
            return Response(status=400)

