from django.core.paginator import Paginator

from yatube.settings import AMOUNT_OF_POSTS


def get_page_obj(request, queryset, argument, amount_of_posts=AMOUNT_OF_POSTS):
    paginator = Paginator(queryset, amount_of_posts)
    page_number = request.GET.get(argument)
    return paginator.get_page(page_number)
