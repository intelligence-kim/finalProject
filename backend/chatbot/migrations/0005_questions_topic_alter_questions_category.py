# Generated by Django 4.2.2 on 2023-08-04 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0004_questions'),
    ]

    operations = [
        migrations.AddField(
            model_name='questions',
            name='topic',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='questions',
            name='category',
            field=models.CharField(max_length=30),
        ),
    ]
