# Generated by Django 4.2.4 on 2024-04-08 06:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Keywords",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("keyword", models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="Pages",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=100)),
                ("url", models.URLField()),
                ("last_modification_date", models.DateTimeField()),
                ("page_size", models.IntegerField()),
                ("child_link_list", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="Indexer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("frequency", models.IntegerField()),
                (
                    "keyword_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="webInterface.keywords",
                    ),
                ),
                (
                    "page_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="webInterface.pages",
                    ),
                ),
            ],
        ),
    ]