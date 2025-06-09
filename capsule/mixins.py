menu = [
    {'title': "Главная", 'url_name': 'index'},
    {'title': "Физические капсулы", 'url_name': 'nature'},
    {'title': "Электронные капсулы", 'url_name': 'electo'},
    {'title': "Регистрация", 'url_name': 'register'},
    {'title': "Вход", 'url_name': 'login'},
]


class DataMixin:
    def get_mixin_context(self, **kwargs):
        context = kwargs
        context['menu'] = menu
        return context



