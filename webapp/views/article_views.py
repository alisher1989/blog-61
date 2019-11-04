from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import urlencode
from django.views.generic import ListView, DetailView, CreateView,\
    UpdateView, DeleteView, FormView
from django.core.paginator import Paginator

from webapp.forms import ArticleForm, ArticleCommentForm, FullSearchForm
from webapp.models import Article, STATUS_ARCHIVED, STATUS_ACTIVE
from .base_views import SimpleSearchView


class IndexView(SimpleSearchView):
    template_name = 'article/index.html'
    context_object_name = 'articles'
    model = Article
    ordering = ['-created_at']
    paginate_by = 5
    paginate_orphans = 1

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['archived_articles'] = self.get_archived_articles()
        return context

    def get_queryset(self):
        return super().get_queryset().filter(status=STATUS_ACTIVE)

    def get_query(self):
        return Q(title__icontains=self.search_query) \
                | Q(author__icontains=self.search_query)

    def get_archived_articles(self):
        return super().get_queryset().filter(status=STATUS_ARCHIVED)


class ArticleSearchView(FormView):
    template_name = 'article/search.html'
    form_class = FullSearchForm

    def form_valid(self, form):
        query = urlencode(form.cleaned_data)
        url = reverse('webapp:search_results') + '?' + query
        return redirect(url)


class SearchResultsView(ListView):
    model = Article
    template_name = 'article/search.html'
    context_object_name = 'articles'
    paginate_by = 5
    paginate_orphans = 2

    def get_queryset(self):
        queryset = super().get_queryset()
        form = FullSearchForm(data=self.request.GET)
        if form.is_valid():
            query = self.get_text_query(form) & self.get_author_query(form)
            queryset = queryset.filter(query).distinct()
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        form = FullSearchForm(data=self.request.GET)
        query = self.get_query_string()
        return super().get_context_data(
            form=form, query=query, object_list=object_list, **kwargs
        )

    def get_query_string(self):
        data = {}
        for key in self.request.GET:
            if key != 'page':
                data[key] = self.request.GET.get(key)
        return urlencode(data)

    def get_author_query(self, form):
        query = Q()
        author = form.cleaned_data.get('author')
        if author:
            article_author = form.cleaned_data.get('article_author')
            if article_author:
                query = query | Q(author__iexact=author)
            comment_author = form.cleaned_data.get('comment_author')
            if comment_author:
                query = query | Q(comments__author__iexact=author)
        return query

    def get_text_query(self, form):
        query = Q()
        text = form.cleaned_data.get('text')
        if text:
            in_title = form.cleaned_data.get('in_title')
            if in_title:
                query = query | Q(title__icontains=text)
            in_text = form.cleaned_data.get('in_text')
            if in_text:
                query = query | Q(text__icontains=text)
            in_tags = form.cleaned_data.get('in_tags')
            if in_tags:
                query = query | Q(tags__name__iexact=text)
            in_comment_text = form.cleaned_data.get('in_comment_text')
            if in_comment_text:
                query = query | Q(comments__text__icontains=text)
        return query


class ArticleView(DetailView):
    template_name = 'article/article.html'
    model = Article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object
        context['form'] = ArticleCommentForm()
        comments = article.comments.order_by('-created_at')
        self.paginate_comments_to_context(comments, context)
        return context

    def paginate_comments_to_context(self, comments, context):
        paginator = Paginator(comments, 3, 0)
        page_number = self.request.GET.get('page', 1)
        page = paginator.get_page(page_number)
        context['paginator'] = paginator
        context['page_obj'] = page
        context['comments'] = page.object_list
        context['is_paginated'] = page.has_other_pages()


class ArticleCreateView(CreateView):
    form_class = ArticleForm
    model = Article
    template_name = 'article/create.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('webapp:article_view', kwargs={'pk': self.object.pk})


class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = Article
    template_name = 'article/update.html'
    form_class = ArticleForm
    context_object_name = 'article'

    def get_success_url(self):
        return reverse('webapp:article_view', kwargs={'pk': self.object.pk})


class ArticleDeleteView(LoginRequiredMixin, DeleteView):
    model = Article
    template_name = 'article/delete.html'
    context_object_name = 'article'
    success_url = reverse_lazy('webapp:index')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.status = STATUS_ARCHIVED
        self.object.save()
        return redirect(self.get_success_url())
