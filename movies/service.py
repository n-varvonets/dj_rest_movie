
def get_client_ip(request):
    """определяем айпи нашего юзера"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip