# Generated by Django 2.2.6 on 2022-12-27 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_auto_20221226_1934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(error_messages={'invalid': 'Заполните поле с текстом'}, verbose_name='Текст поста'),
        ),
    ]
