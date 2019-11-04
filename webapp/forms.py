from django import forms
from django.core.exceptions import ValidationError

from webapp.models import Article, Comment, STATUS_ACTIVE


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ['created_at', 'updated_at', 'status']

    def clean_title(self):
        title = self.cleaned_data['title']
        min_length = 10
        if len(title) < min_length:
            raise ValidationError(
                'Title should be at least %(length)s symbols long.',
                code='title_too_short',
                params={'length': min_length}
            )
        return title.capitalize()

    def clean(self):
        super().clean()
        title = self.cleaned_data.get('title', '')
        text = self.cleaned_data.get('text', '')
        if title.lower() == text.lower():
            raise ValidationError('Text should not duplicate title')
        return self.cleaned_data


class CommentForm(forms.ModelForm):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['article'].queryset = Article.objects.filter(status=STATUS_ACTIVE)

    # article = forms.ModelChoiceField(queryset=Article.objects.filter(status=STATUS_ACTIVE), label='Статья')

    class Meta:
        model = Comment
        exclude = ['created_at', 'updated_at']


class ArticleCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['author', 'text']


class SimpleSearchForm(forms.Form):
    search = forms.CharField(max_length=100, required=False, label='Найти')


class FullSearchForm(forms.Form):
    text = forms.CharField(max_length=100, required=False, label='Текст')
    in_title = forms.BooleanField(initial=True, required=False, label='В заголовках')
    in_text = forms.BooleanField(initial=True, required=False, label='В тексте')
    in_tags = forms.BooleanField(initial=True, required=False, label='В тегах')
    in_comment_text = forms.BooleanField(initial=False, required=False, label='В тексте комментариев')

    author = forms.CharField(max_length=100, required=False, label='Автор')
    in_articles = forms.BooleanField(initial=True, required=False, label='Статей')
    in_comments = forms.BooleanField(initial=False, required=False, label='Комментариев')

    def clean(self):
        super().clean()
        data = self.cleaned_data
        text = data.get('text')
        author = data.get('author')
        if not (text or author):
            raise ValidationError('No search text or author provided',
                                  code='text_and_author_empty')
        errors = []
        if text:
            in_title = data.get('in_title')
            in_text = data.get('in_text')
            in_tags = data.get('in_tags')
            in_comment_text = data.get('in_comment_text')
            if not (in_title or in_text or in_tags or in_comment_text):
                errors.append(ValidationError(
                    'One of the checkboxes should be checked: In title, In text, In tags, In comment text',
                    code='text_search_criteria_empty'
                ))
        if author:
            in_articles = data.get('in_articles')
            in_comments = data.get('in_comments')
            if not (in_articles or in_comments):
                errors.append(ValidationError(
                    'One of the checkboxes should be checked: In articles, In comments',
                    code='author_search_criteria_empty'
                ))
        if errors:
            raise ValidationError(errors)
        return data
