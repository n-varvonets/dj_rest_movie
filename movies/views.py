from django.db import models
from rest_framework import generics, permissions, viewsets
from .service import get_client_ip, MovieFilter
from .serializers import *
from django_filters.rest_framework import DjangoFilterBackend


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    """вывод списка фильмов и полного фильма реализовано в одном классе при помощи viewsets"""

    """как и в generic описываем"""
    filter_backends = (DjangoFilterBackend, )  # 3.1) к нашему классу подключаем фильтры джанго. Теперь в сервисах нужно написать классы "как и что нужно фильтровать"
    filterset_class = MovieFilter  # 3.2)  теперь указыв поля филтрации в сервисе передаем эти данные в переменную

    """как и  generic  получаем наш """
    def get_queryset(self):
        movies = Movie.objects.filter(draft=False).annotate(
            rating_user=models.Count(
                'ratings', filter=models.Q(ratings__ip=get_client_ip(self.request))  # 2)compared with APIView - request мы уже забираем из self
            )
        ).annotate(
            middle_star=models.Sum(models.F('ratings__star')) / models.Count(models.F('ratings')))
        return movies

    """ т.к. для списка фильмов и одной записи мы используем разные сериализаторы,
     то укажем это  переопределив метод get_serializer_class """
    def get_serializer_class(self):
        if self.action == "list":
            return MovieListSerializer
        elif self.action == "retrieve":
            return MovieDetailSerializer


class ReviewCreateViewSet(viewsets.ModelViewSet):  # ModelViewSet позволяет нам:
    # добавлять запись(1), выводить список(all), обновлять(1) и удалять(1) запись
    """добавление отзыва к фильму (просто указав сериализатор)
    но т.к. по преполгаемуому функционалу отзыва мы можем только добавлять его или выводить весь список,
    то урлс при post запросе будет вызываться метод create"""
    serializer_class = ReviewCreateSerializer


class AddStarRatingViewSet(viewsets.ModelViewSet):
    """Добавление рейтинга к фильму"""
    serializer_class = CreateRatingSerializer

    def perform_create(self, serializer):
        serializer.save(ip=get_client_ip(self.request))


class ActorsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вывод актеров или режисеров"""
    queryset = Actor.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return ActorListSerializer
        elif self.action == "retrieve":
            return ActorDetailSerializer


"""-------------------------------классы на основе generics--------------------------------------"""

# class MovieListView(generics.ListAPIView):
#     """вывод списка фильмов с помщью уже generics"""
#
#     serializer_class = MovieListSerializer  # 1)нашу сериализацю уже указываем как атрибут а не в методе
#
#     filter_backends = (DjangoFilterBackend, )  # 3.1) к нашему классу подключаем фильтры джанго. Теперь в сервисах нужно написать классы "как и что нужно фильтровать"
#     filterset_class = MovieFilter  # 3.2)  теперь указыв поля филтрации в сервисе передаем эти данные в переменную
#
#     # 4) добавим атрибут указываищий права доступа пользовталя для просмотра данного урл
#     # 4.1) без токена - http://i.imgur.com/HHLw2PK.png
#     # 4.2) с токеном в хидере - http://i.imgur.com/XbZr8xj.png
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_queryset(self):
#         movies = Movie.objects.filter(draft=False).annotate(
#             rating_user=models.Count(
#                 'ratings', filter=models.Q(ratings__ip=get_client_ip(self.request))  # 2)compared with APIView - request мы уже забираем из self
#             )
#         ).annotate(
#             middle_star=models.Sum(models.F('ratings__star')) / models.Count(models.F('ratings')))
#         return movies
#
#
# class MovieDetailView(generics.RetrieveAPIView):
#     """вывод полного филмьа"""
#     queryset = Movie.objects.filter(draft=False)  # класс RetrieveAPIView сам подставит поиск по  pk
#     serializer_class = MovieDetailSerializer
#
#
# class ReviewCreateView(generics.CreateAPIView):
#     """вывод полного филмьа. было - http://i.imgur.com/b0jDcnJ.png, стало - http://i.imgur.com/J2Tr8RV.png"""
#     serializer_class = ReviewCreateSerializer
#
#     # {
#     # "email": "test@gmail.com",
#     # "name": "Mike",
#     # "text": "some text",
#     # "movie": 2
#     # }
#
#
# class AddStarRatingView(generics.CreateAPIView):
#     """Добавление рейтинга фильму"""
#
#     serializer_class = CreateRatingSerializer
#
#     def perform_create(self, serializer):
#         """нам при сохраненинии нашей сериализации нужно добавлять айпи адресс нашего пользователя.
#         данный метод принимает нашу серилизацию и в метод save  мы можем указать дополнительно те парметры, которые хотим сохранить"""
#         serializer.save(ip=get_client_ip(self.request))  # request мы уже получаем через self
#
#
# """суть generic в том что мы можем с легкостью описать логику, которую хотим вывести...
# мы должны указать всего лишь два аттрибута: queryset и классы реализации"""
# class ActorsListView(generics.ListAPIView):
#     """Вывод списка актёров/режисеров +"""
#     queryset = Actor.objects.all()
#     serializer_class = ActorListSerializer  # мы просто указываем имя, а не вызываем.. так что без скобок
#
#
# class ActorsDetailView(generics.RetrieveAPIView):  # RetrieveAPIView - аналог класса DetailView  в простом джанго
#     """Вывод полного описания актера и режисера"""
#     queryset = Actor.objects.all()
#     serializer_class = ActorDetailSerializer



"""-------------------------------изначальный вид класов бзе  generics--------------------------------------"""

# class MovieListView(APIView):
#     """вывод списка фильмов"""
#
#     def get(self, request):
#         # movies = Movie.objects.filter(draft=False)
#         """1) при выводе списка наших фильмов у нас было некое поле(говрящее о том пользователь установил ли рейтинг к фильму или нет)"""
#         # movies = Movie.objects.filter(draft=False).annotate(
#         #     rating_user=models.Case(  # rating_user  будет автоматически добавлено каждому обьекту movie
#         #         models.When(
#         #             ratings__ip=get_client_ip(request), then=True),  # ratings - related name of model Rating и если в
#         #         # таблице Rating есть айпи нашего клиенто, то возврщаем этому полю  True
#         #         default=False,  # если нет, то  False
#         #         output_field=models.BooleanField()
#         #     )
#         # )  # но минус такого подхода что выводяться записи там где rating_user наш  и False...
#         # т.е. добавлеен рейтинг от другого пользователя(http://i.imgur.com/HYnBLR5.png).... его нужно удалить
#         """2)есть еще один подход"""
#         movies = Movie.objects.filter(draft=False).annotate(
#             rating_user=models.Count(  # методом  Count мы будем подсчитывать кол-во установленных нашим пользователем
#                 # рейтингов к фильму. Т.к. мы знаем что кол-во устновленных рейтингов к фильму можно только один раз,
#                 # то будет возращена нам еденица(True) либо ноль(False)
#                 'ratings', filter=models.Q(ratings__ip=get_client_ip(request))
#             )
#         ).annotate(
#             middle_star=models.Sum(models.F('ratings__star')) / models.Count(models.F('ratings'))  # общую сумму звезд рейтинга мы будем делить на кол-во проголосовавших(наших записей)
#         )
#
#         # в переменную сериалайзер мы будем заносить работу нашего сириализатора
#         serializer = MovieListSerializer(movies,
#                                          many=True)  # movies - передаем туда наш  queryset, many=True - гвоорит о том что у нас будет несколько записей
#         return Response(serializer.data)



# class MovieDetailView(APIView):
#     """вывод полного филмьа"""
#
#     def get(self, request, pk):
#         # из бд забирает обьект
#         movie = Movie.objects.get(id=pk, draft=False)
#         # в переменную сериалайзер мы будем заносить работу нашего сириализатора
#         serializer = MovieDetailSerializer(
#             movie)  # movies - передаем туда наш  queryset, many=True - гвоорит о том что у нас будет несколько записей
#         return Response(serializer.data)


# class ReviewCreateView(APIView):
#     """вывод полного филмьа  """
#
#     def post(self, request):
#         review = ReviewCreateSerializer(data=request.data)  # передаем наши поля с клиентского запроса request.data
#         if review.is_valid():
#             review.save()
#         return Response(status=201)



# class AddStarRatingView(APIView):
#     """Добавление рейтинга фильму"""
#
#     def post(self, request):
#         serializer = CreateRatingSerializer(data=request.data)
#         if serializer.is_valid():
#             # serializer.save(ip=self.get_client_ip(request)) т.к. мы перенсли  get_client_ip в service
#             serializer.save(ip=get_client_ip(request))
#             return Response(status=201)
#         else:
#             return Response(status=400)
