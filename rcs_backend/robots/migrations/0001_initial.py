# Generated by Django 4.2.15 on 2024-08-26 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Robot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('robotID', models.CharField(max_length=100, unique=True)),
                ('battery', models.FloatField()),
                ('last2Dcode', models.CharField(max_length=100)),
                ('mapID', models.CharField(max_length=100)),
                ('orientation', models.FloatField()),
                ('payload', models.FloatField()),
                ('position', models.CharField(max_length=100)),
                ('speed', models.FloatField()),
                ('state', models.CharField(max_length=50)),
                ('taskID', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
    ]
