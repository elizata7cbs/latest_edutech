# Generated by Django 4.2.14 on 2024-08-01 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserGroup',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('groupID', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField()),
                ('dateCreated', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(default=1)),
            ],
        ),
    ]
