from django.db import models
from rest_framework.response import Response
from rest_framework.views import APIView
from .service import *
from .models import Movie
from .serializers import *


class MovieListView(APIView):
    """вывод списка фильмов"""

    def get(self, request):
        # movies = Movie.objects.filter(draft=False)
        """1) при выводе списка наших фильмов у нас было некое поле(говрящее о том пользователь установил ли рейтинг к фильму или нет)"""
        # movies = Movie.objects.filter(draft=False).annotate(
        #     rating_user=models.Case(  # rating_user  будет автоматически добавлено каждому обьекту movie
        #         models.When(
        #             ratings__ip=get_client_ip(request), then=True),  # ratings - related name of model Rating и если в
        #         # таблице Rating есть айпи нашего клиенто, то возврщаем этому полю  True
        #         default=False,  # если нет, то  False
        #         output_field=models.BooleanField()
        #     )
        # )  # но минус такого подхода что выводяться записи там где rating_user наш  и False...
        # т.е. добавлеен рейтинг от другого пользователя(http://i.imgur.com/HYnBLR5.png).... его нужно удалить
        """2)есть еще один подход"""
        movies = Movie.objects.filter(draft=False).annotate(
            rating_user=models.Count(  # методом  Count мы будем подсчитывать кол-во установленных нашим пользователем
                # рейтингов к фильму. Т.к. мы знаем что кол-во устновленных рейтингов к фильму можно только один раз,
                # то будет возращена нам еденица(True) либо ноль(False)
                'ratings', filter=models.Q(ratings__ip=get_client_ip(request))
            )
        ).annotate(
            middle_star=models.Sum(models.F('ratings__star')) / models.Count(models.F('ratings'))  # общую сумму звезд рейтинга мы будем делить на кол-во проголосовавших(наших записей)
        )

        # в переменную сериалайзер мы будем заносить работу нашего сириализатора
        serializer = MovieListSerializer(movies,
                                         many=True)  # movies - передаем туда наш  queryset, many=True - гвоорит о том что у нас будет несколько записей
        return Response(serializer.data)


class MovieDetailView(APIView):
    """вывод полного филмьа"""

    def get(self, request, pk):
        # из бд забирает обьект
        movie = Movie.objects.get(id=pk, draft=False)
        # в переменную сериалайзер мы будем заносить работу нашего сириализатора
        serializer = MovieDetailSerializer(
            movie)  # movies - передаем туда наш  queryset, many=True - гвоорит о том что у нас будет несколько записей
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

    def post(self, request):
        serializer = CreateRatingSerializer(data=request.data)
        if serializer.is_valid():
            # serializer.save(ip=self.get_client_ip(request)) т.к. мы перенсли  get_client_ip в service
            serializer.save(ip=get_client_ip(request))
            return Response(status=201)
        else:
            return Response(status=400)
