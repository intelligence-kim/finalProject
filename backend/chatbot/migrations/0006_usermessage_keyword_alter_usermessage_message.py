# Generated by Django 4.2.2 on 2023-08-08 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0005_questions_topic_alter_questions_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermessage',
            name='keyword',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='usermessage',
            name='message',
            field=models.CharField(max_length=500),
        ),
    ]
