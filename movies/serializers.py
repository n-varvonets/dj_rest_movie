from rest_framework import serializers

from .models import Movie, Review, Rating


class MovieListSerializer(serializers.ModelSerializer):
    """Список фильмов"""

    class Meta:
        model = Movie
        # как и форме указываю поля, которые хочу выводить
        fields = ("title", "tagline", "category")


class ReviewCreateSerializer(serializers.ModelSerializer):
    """добавление отзыва"""

    class Meta:
        model = Review
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

    # что бы при выводу данных http://i.imgur.com/5nbJn5d.png отобржались вместо related полей отображалиссь не их  id,
    # а их названия, то пропишем для них сериализаторы
    category = serializers.SlugRelatedField(slug_field="name", read_only=True)
    directors = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)
    actors = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)
    genres = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)

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
        )
        return rating

    # {
    # "star": 3,
    # "movie":2
    # }


