from django.urls import reverse

UNEXISTING_PAGE_URL = '/unexisting_page/'
INDEX_URL = '/'
INDEX_REVERSE = reverse('posts:index')
CREATE_URL = '/create/'
CREATE_REVERSE = reverse('posts:post_create')
