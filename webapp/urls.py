from django.urls import path
from webapp.views import IndexView, ArticleView, ArticleCreateView, \
    ArticleUpdateView, ArticleDeleteView, CommentCreateView, CommentForArticleCreateView, \
    CommentListView, CommentUpdateView, CommentDeleteView, ArticleSearchView, \
    SearchResultsView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('article/<int:pk>/', ArticleView.as_view(), name='article_view'),
    path('article/add/', ArticleCreateView.as_view(), name='article_add'),
    path('article/<int:pk>/edit/', ArticleUpdateView.as_view(), name='article_update'),
    path('article/<int:pk>/delete/', ArticleDeleteView.as_view(), name='article_delete'),
    path('article/search/', ArticleSearchView.as_view(), name='article_search'),
    path('article/search/results/', SearchResultsView.as_view(), name='search_results'),
    path('comments/', CommentListView.as_view(), name='comment_list'),
    path('comment/add/', CommentCreateView.as_view(), name='comment_add'),
    path('comment/<int:pk>/edit/', CommentUpdateView.as_view(), name='comment_update'),
    path('comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment_delete'),
    path('article/<int:pk>/add-comment/', CommentForArticleCreateView.as_view(), name='article_comment_create'),
]

app_name = 'webapp'
