# Generated by Django 2.2.5 on 2019-10-16 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0006_article_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('archived', 'Archived')], default='active', max_length=20, verbose_name='Статус'),
        ),
    ]
