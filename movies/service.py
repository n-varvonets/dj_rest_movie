from django_filters import rest_framework as filters
from .models import Movie


def get_client_ip(request):
    """определяем айпи нашего юзера"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class CharFilterFilter(filters.BaseInFilter, filters.CharFilter):
    """т.к. жанры - это M2M(есть третья связная таблица,которая ищет по id,а не по имени http://i.imgur.com/QJNndnN.png)
     и нам нужно искать в диапазоне именно имён(боевики, приключения...), функционал текст.значения описан в CharFilter.
    т.е. нам нужно использовать 'in' во фильтрации, логика которого прописана в BaseInFilter """
    pass


class MovieFilter(filters.FilterSet):
    genres = CharFilterFilter(field_name='genres__name', lookup_expr='in')  # lookup_expr='in' - данное поле мы будем
    # фильтровать по методу вхождения('in') - http://i.imgur.com/ykqgSLn.png ?year_min=2000&year_max=2013&genres=Ужасы

    year = filters.RangeFilter()  # у нас года будут - диапазон дат (от year_min=''&year_max='' - http://i.imgur.com/o1dQfQj.png)

    class Meta:
        model = Movie
        fields = ['genres', 'year']