from rest_framework import serializers

from .models import Movie, Review, Rating, Actor


class MovieListSerializer(serializers.ModelSerializer):
    """Список фильмов"""

    # добавим поле для просмотра на то оставил ли пользова тель рейтинг фильму или нет
    rating_user = serializers.BooleanField()
    middle_star = serializers.FloatField()

    class Meta:
        model = Movie
        # как и форме указываю поля, которые хочу выводить
        fields = ("id", "title", "tagline", "category", "rating_user", 'middle_star')


class ReviewCreateSerializer(serializers.ModelSerializer):
    """добавление отзыва"""

    class Meta:
        model = Review
        fields = '__all__'


class ActorListSerializer(serializers.ModelSerializer):
    """Вывод списка актеров и режисеров"""

    class Meta:
        model = Actor
        fields = ('id', 'name', 'image')


class ActorDetailSerializer(serializers.ModelSerializer):
    """Вывод полного описания актера и режисера"""

    class Meta:
        model = Actor
        fields = '__all__'



class FilterReviewListSerializer(serializers.ListSerializer):
    """Фильтр комментариев, только parents"""

    def to_representation(self, data):
        data = data.filter(parent=None)
        return super().to_representation(data)


class RecursiveSerializer(serializers.Serializer):
        """вывод рекурсивно children"""

        def to_representation(self, value):  # value - значение одной записи из бд
            """ищем всех наших детей, которые завязаны на нашем отзыве"""
            # serializer = self.parent.parent.__class__(value, context=self.context)  # Берет екземпляр сериализатора
            # parent который есть ListSerializer (он появился изза того что мы передали many=True в RecursiveSerializer)
            # после етого он берет parent екземпляр нашего parenta и достает сылку на его клас

            serializer = ReviewSerializer(value, context=self.context)  #  делает то же самое что и выше метод

            return serializer.data


class ReviewSerializer(serializers.ModelSerializer):
    # TODO разобраться как работает вывод рекурсии, а то с первого раза не понял
    """вывод отзывов"""
    # 1) мы сначала должны выводить родительские отзывы, а потом вложенность дочерних
    # 2) для этого дабавим поле children, которое будем подставлять вместо поля парент
    children = RecursiveSerializer(many=True)

    class Meta:
        """ для того что бы достать наших детей,то нужно в модели к нашем полю parent мы должны добавить related_name"""
        model = Review
        fields = ('name', 'text', 'children')

        #  что бы сидрен отзыв не дублировался добавим атрибут,
        list_serializer_class = FilterReviewListSerializer


class MovieDetailSerializer(serializers.ModelSerializer):
    """Детали фильма"""

    # 0.1) что бы при выводу данных http://i.imgur.com/5nbJn5d.png отобржались вместо related полей отображалиссь
    # 0.2) не их  id, а их названия, то пропишем для них сериализаторы
    category = serializers.SlugRelatedField(slug_field="name", read_only=True)
    genres = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)


    #  3) сейчас в деталях к фильму выводяться только имена актеров/режимсеров(http://i.imgur.com/SGkPV8X.png),
    # directors = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)
    # actors = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)
    #  4) но т.к. мы только что написали сериализатор с деталями к актеру/режисеру, то вывеодим их к шашему фильму
    directors = ActorListSerializer(read_only=True, many=True)
    actors = ActorListSerializer(read_only=True, many=True)


    # 1)можно добавить поле таким образом, но может упасть ошибка(http://i.imgur.com/NxIjG54.png),
    # т.к. в модели Movie отсутвует related field review
    # 2) поэтмоу в модели  Review так и добавим  related_name="reviews"...
    # т.е. из таблицы ревью берем все записи по related_name и переносим в наш модулю для отображения
    # reviews = ReviewCreateSerializer(many=True)  # можно и таким методом.. джанго позволить нам,но метод только с пост
    reviews = ReviewSerializer(many=True)

    class Meta:
        model = Movie
        # т.к. класс муви имеет дофига атрибутов, то можно указать какие поля не выводить, а остальные автоматом покажут
        exclude = ("draft", "tagline")


class CreateRatingSerializer(serializers.ModelSerializer):
    """добавление рейтинга пользователем"""

    class Meta:
        model = Rating
        fields = ("star", "movie")

    def create(self, validated_data):  # validated_data - данные, которые мы передадаем в
        # сериализатор от клиентской стороны и обновлять мы будем поле star
        rating = Rating.objects.update_or_create(
            ip=validated_data.get('ip', None),
            movie=validated_data.get('movie', None),
            defaults={'star': validated_data.get('star')},
        )  # что бы избежать ошибки Original exception text was: 'tuple' object has no attribute 'star'.
        # http://i.imgur.com/StxlnVT.png - то наш кортеж мы разложим на два элемента. (наш обьект будет передаваться в
        # rating, а  True/False - в переменную _ )
        return rating

    # {
    # "star": 3,
    # "movie":2
    # }


