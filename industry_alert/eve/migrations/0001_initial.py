# Generated by Django 3.2.5 on 2022-04-12 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InvTypes',
            fields=[
                ('typeId', models.IntegerField(primary_key=True, serialize=False)),
                ('groupId', models.IntegerField()),
                ('typeName', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('mass', models.FloatField()),
                ('volume', models.FloatField()),
                ('capacity', models.FloatField()),
                ('portionsize', models.IntegerField()),
                ('raceId', models.IntegerField()),
                ('basePrice', models.DecimalField(decimal_places=4, max_digits=19)),
                ('published', models.IntegerField()),
                ('marketGroupId', models.IntegerField()),
                ('iconId', models.IntegerField()),
                ('soundId', models.IntegerField()),
                ('graphicId', models.IntegerField()),
            ],
            options={
                'db_table': 'invTypes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='RamActivity',
            fields=[
                ('activityId', models.IntegerField(primary_key=True, serialize=False)),
                ('activityName', models.CharField(max_length=100)),
                ('iconNo', models.CharField(max_length=5)),
                ('description', models.CharField(max_length=1000)),
                ('published', models.BooleanField()),
            ],
            options={
                'db_table': 'ramActivities',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SolarSystem',
            fields=[
                ('regionID', models.IntegerField()),
                ('constellationID', models.IntegerField()),
                ('solarSystemID', models.IntegerField(primary_key=True, serialize=False)),
                ('solarSystemName', models.CharField(max_length=100)),
                ('x', models.FloatField()),
                ('y', models.FloatField()),
                ('z', models.FloatField()),
                ('xMin', models.FloatField()),
                ('xMax', models.FloatField()),
                ('yMin', models.FloatField()),
                ('yMax', models.FloatField()),
                ('zMin', models.FloatField()),
                ('zMax', models.FloatField()),
                ('luminosity', models.FloatField()),
                ('border', models.BooleanField()),
                ('fringe', models.BooleanField()),
                ('corridor', models.BooleanField()),
                ('hub', models.BooleanField()),
                ('international', models.BooleanField()),
                ('regional', models.BooleanField()),
                ('constellation', models.BooleanField()),
                ('security', models.FloatField()),
                ('factionID', models.IntegerField()),
                ('radius', models.FloatField()),
                ('sunTypeId', models.IntegerField()),
                ('securityClass', models.CharField(max_length=2)),
            ],
            options={
                'db_table': 'mapSolarSystems',
                'managed': False,
            },
        ),
    ]
