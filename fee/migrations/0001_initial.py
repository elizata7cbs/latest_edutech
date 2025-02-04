# Generated by Django 4.2.7 on 2024-09-17 11:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('students', '0001_initial'),
        ('feecategories', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentFeeCategories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fee_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='feecategories.feecategories')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.students')),
            ],
            options={
                'db_table': 'StudentFeeCategories',
            },
        ),
        migrations.CreateModel(
            name='FeeCategoryTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255)),
                ('debit', models.DecimalField(decimal_places=2, max_digits=10)),
                ('credit', models.DecimalField(decimal_places=2, max_digits=10)),
                ('balance', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('transaction_date', models.DateField(auto_now_add=True)),
                ('firstName', models.CharField(blank=True, max_length=255)),
                ('middleName', models.CharField(blank=True, max_length=255)),
                ('feecategory', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='feecategories.feecategories')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.students')),
            ],
            options={
                'db_table': 'fee_category_transactions',
            },
        ),
    ]
