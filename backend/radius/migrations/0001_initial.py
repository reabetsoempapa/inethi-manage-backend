# Generated by Django 5.0.7 on 2024-08-13 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Nas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nasname', models.CharField(max_length=128)),
                ('shortname', models.CharField(blank=True, max_length=32, null=True)),
                ('nasidentifier', models.CharField(max_length=64)),
                ('type', models.CharField(blank=True, max_length=30, null=True)),
                ('ports', models.IntegerField(blank=True, null=True)),
                ('secret', models.CharField(max_length=60)),
                ('server', models.CharField(blank=True, max_length=64, null=True)),
                ('community', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.CharField(blank=True, max_length=200, null=True)),
                ('connection_type', models.CharField(blank=True, max_length=7, null=True)),
                ('timezone', models.CharField(max_length=255)),
                ('record_auth', models.IntegerField()),
                ('ignore_acct', models.IntegerField()),
                ('dynamic_attribute', models.CharField(max_length=50)),
                ('dynamic_value', models.CharField(max_length=50)),
                ('monitor', models.CharField(blank=True, max_length=9, null=True)),
                ('ping_interval', models.IntegerField()),
                ('heartbeat_dead_after', models.IntegerField()),
                ('last_contact', models.DateTimeField(blank=True, null=True)),
                ('session_auto_close', models.IntegerField()),
                ('session_dead_time', models.IntegerField()),
                ('on_public_maps', models.IntegerField()),
                ('lat', models.FloatField(blank=True, null=True)),
                ('lon', models.FloatField(blank=True, null=True)),
                ('photo_file_name', models.CharField(max_length=128)),
                ('cloud_id', models.IntegerField(blank=True, null=True)),
                ('created', models.DateTimeField()),
                ('modified', models.DateTimeField()),
            ],
            options={
                'db_table': 'nas',
            },
        ),
        migrations.CreateModel(
            name='Radacct',
            fields=[
                ('radacctid', models.BigAutoField(primary_key=True, serialize=False)),
                ('acctsessionid', models.CharField(max_length=64)),
                ('acctuniqueid', models.CharField(max_length=32, unique=True)),
                ('username', models.CharField(max_length=64)),
                ('groupname', models.CharField(max_length=64)),
                ('realm', models.CharField(blank=True, max_length=64, null=True)),
                ('nasipaddress', models.CharField(max_length=15)),
                ('nasidentifier', models.CharField(max_length=64)),
                ('nasportid', models.CharField(blank=True, max_length=15, null=True)),
                ('nasporttype', models.CharField(blank=True, max_length=32, null=True)),
                ('acctstarttime', models.DateTimeField(blank=True, null=True)),
                ('acctupdatetime', models.DateTimeField(blank=True, null=True)),
                ('acctstoptime', models.DateTimeField(blank=True, null=True)),
                ('acctinterval', models.IntegerField(blank=True, null=True)),
                ('acctsessiontime', models.PositiveIntegerField(blank=True, null=True)),
                ('acctauthentic', models.CharField(blank=True, max_length=32, null=True)),
                ('connectinfo_start', models.CharField(blank=True, max_length=50, null=True)),
                ('connectinfo_stop', models.CharField(blank=True, max_length=50, null=True)),
                ('acctinputoctets', models.BigIntegerField(blank=True, null=True)),
                ('acctoutputoctets', models.BigIntegerField(blank=True, null=True)),
                ('calledstationid', models.CharField(max_length=50)),
                ('callingstationid', models.CharField(max_length=50)),
                ('acctterminatecause', models.CharField(max_length=32)),
                ('servicetype', models.CharField(blank=True, max_length=32, null=True)),
                ('framedprotocol', models.CharField(blank=True, max_length=32, null=True)),
                ('framedipaddress', models.CharField(max_length=15)),
                ('acctstartdelay', models.IntegerField(blank=True, null=True)),
                ('acctstopdelay', models.IntegerField(blank=True, null=True)),
                ('xascendsessionsvrkey', models.CharField(blank=True, max_length=20, null=True)),
                ('operator_name', models.CharField(max_length=32)),
            ],
            options={
                'db_table': 'radacct',
            },
        ),
        migrations.CreateModel(
            name='Radcheck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=64)),
                ('attribute', models.CharField(max_length=64)),
                ('op', models.CharField(max_length=2)),
                ('value', models.CharField(max_length=253)),
            ],
            options={
                'db_table': 'radcheck',
            },
        ),
        migrations.CreateModel(
            name='Radgroupcheck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('groupname', models.CharField(max_length=64)),
                ('attribute', models.CharField(max_length=64)),
                ('op', models.CharField(max_length=2)),
                ('value', models.CharField(max_length=253)),
                ('comment', models.CharField(max_length=253)),
                ('created', models.DateTimeField()),
                ('modified', models.DateTimeField()),
            ],
            options={
                'db_table': 'radgroupcheck',
            },
        ),
        migrations.CreateModel(
            name='Radgroupreply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('groupname', models.CharField(max_length=64)),
                ('attribute', models.CharField(max_length=64)),
                ('op', models.CharField(max_length=2)),
                ('value', models.CharField(max_length=253)),
                ('comment', models.CharField(max_length=253)),
                ('created', models.DateTimeField()),
                ('modified', models.DateTimeField()),
            ],
            options={
                'db_table': 'radgroupreply',
            },
        ),
        migrations.CreateModel(
            name='Radippool',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pool_name', models.CharField(max_length=30)),
                ('framedipaddress', models.CharField(max_length=15)),
                ('nasipaddress', models.CharField(max_length=15)),
                ('calledstationid', models.CharField(max_length=30)),
                ('callingstationid', models.CharField(max_length=30)),
                ('expiry_time', models.DateTimeField(blank=True, null=True)),
                ('username', models.CharField(max_length=64)),
                ('pool_key', models.CharField(max_length=30)),
                ('nasidentifier', models.CharField(max_length=64)),
                ('extra_name', models.CharField(max_length=100)),
                ('extra_value', models.CharField(max_length=100)),
                ('active', models.IntegerField()),
                ('permanent_user_id', models.IntegerField(blank=True, null=True)),
                ('created', models.DateTimeField()),
                ('modified', models.DateTimeField()),
            ],
            options={
                'db_table': 'radippool',
            },
        ),
        migrations.CreateModel(
            name='Radpostauth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=64)),
                ('realm', models.CharField(blank=True, max_length=64, null=True)),
                ('pass_field', models.CharField(db_column='pass', max_length=64)),
                ('reply', models.CharField(max_length=32)),
                ('nasname', models.CharField(max_length=128)),
                ('authdate', models.DateTimeField()),
            ],
            options={
                'db_table': 'radpostauth',
            },
        ),
        migrations.CreateModel(
            name='Radreply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=64)),
                ('attribute', models.CharField(max_length=64)),
                ('op', models.CharField(max_length=2)),
                ('value', models.CharField(max_length=253)),
            ],
            options={
                'db_table': 'radreply',
            },
        ),
        migrations.CreateModel(
            name='Radusergroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=64)),
                ('groupname', models.CharField(max_length=64)),
                ('priority', models.IntegerField()),
            ],
            options={
                'db_table': 'radusergroup',
            },
        ),
    ]
