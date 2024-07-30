# Generated by Django 5.0.6 on 2024-07-30 09:22

import django.db.models.deletion
import macaddress.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Mesh',
            fields=[
                ('name', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('lat', models.FloatField(default=0.0)),
                ('lon', models.FloatField(default=0.0)),
            ],
            options={
                'verbose_name_plural': 'meshes',
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(max_length=100, unique=True)),
                ('name', models.CharField(max_length=20, unique=True)),
                ('service_type', models.CharField(choices=[('utility', 'utility'), ('entertainment', 'entertainment'), ('games', 'games'), ('education', 'education')], max_length=20)),
                ('api_location', models.CharField(choices=[('cloud', 'cloud'), ('local', 'local')], max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='WlanConf',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('passphrase', models.CharField(blank=True, max_length=100, null=True)),
                ('security', models.CharField(choices=[('open', 'Open'), ('wpapsk', 'WPA-PSK')], max_length=6)),
                ('is_guest', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('mac', macaddress.fields.MACAddressField(help_text='Physical MAC address', integer=True, primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='Unique device name', max_length=255, unique=True)),
                ('adopted_at', models.DateTimeField(blank=True, help_text='The date & time that this device was adopted into its mesh', null=True)),
                ('last_contact', models.DateTimeField(blank=True, help_text='The time of last active contect', null=True)),
                ('last_ping', models.DateTimeField(blank=True, help_text='The time that this device was last pinged by the server', null=True)),
                ('is_ap', models.BooleanField(default=False, help_text='Determines whether this device is an AP (Access Point) which clients can connect to, or a mesh node that connects other nodes')),
                ('nas_name', models.CharField(blank=True, help_text='The name of the NAS device for this node', max_length=128, null=True)),
                ('reachable', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('unknown', 'Unknown'), ('offline', 'Offline'), ('online', 'Online'), ('rebooting', 'Rebooting')], default='unknown', help_text='The online status of this device', max_length=16)),
                ('health_status', models.CharField(choices=[('unknown', 'Unknown'), ('critical', 'Critical'), ('warning', 'Warning'), ('decent', 'Decent'), ('ok', 'Ok')], default='unknown', help_text='The health status of this node. Even devices that are online way not be functioning correctly', max_length=16)),
                ('reboot_flag', models.BooleanField(default=False, help_text='Will reboot the device the next time it tries to contact the server')),
                ('description', models.CharField(blank=True, help_text='A user-friendly description of this device', max_length=255, null=True)),
                ('hardware', models.CharField(choices=[('ubnt_ac_mesh', 'Ubiquiti AC Mesh'), ('tl_eap225_3_o', 'TPLink EAP')], default='tl_eap225_3_o', help_text='The physical device type', max_length=255)),
                ('ip', models.CharField(blank=True, help_text='The IP address of the device in the network', max_length=255, null=True)),
                ('lat', models.FloatField(blank=True, help_text='Geographical device latitude', null=True)),
                ('lon', models.FloatField(blank=True, help_text='Geographical device longitude', null=True)),
                ('created', models.DateTimeField(auto_now_add=True, help_text='The date & time this device was created')),
                ('mesh', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='monitoring.mesh')),
                ('neighbours', models.ManyToManyField(blank=True, help_text='Neighbouring nodes in the mesh', to='monitoring.node')),
            ],
        ),
        migrations.CreateModel(
            name='ClientSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mac', macaddress.fields.MACAddressField(integer=True)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('bytes_recv', models.IntegerField()),
                ('bytes_sent', models.IntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to=settings.AUTH_USER_MODEL)),
                ('uplink', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client_sessions', to='monitoring.node')),
            ],
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.SmallIntegerField(choices=[(1, 'Warning'), (2, 'ERROR'), (3, 'Critical')])),
                ('title', models.CharField(max_length=100)),
                ('text', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('resolved', models.BooleanField(default=False)),
                ('node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alerts', to='monitoring.node')),
            ],
        ),
        migrations.AddField(
            model_name='mesh',
            name='wlanconfs',
            field=models.ManyToManyField(blank=True, to='monitoring.wlanconf'),
        ),
    ]
