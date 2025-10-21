from django.urls import path
from .views import SearchHistoryListView, SearchHistoryCreateView

urlpatterns = [
    path('search-history/list/', SearchHistoryListView.as_view(), name='search-history-list'),
    path('search-history/create/', SearchHistoryCreateView.as_view(), name='search-history-create'),
]