"""Auto-generated models from the freeradius database.

As far as I can tell, radiusdesk has taken the original database models
from freeradius and extended them for its own purposes. These are table
definitions based on radiusdesk's modified version of freeradius.

The original sql definitions are in /etc/freeradius/x.x/mods-config/sql/main/sqlite
"""

from django.db import models


class Radacct(models.Model):
    radacctid = models.BigAutoField(primary_key=True)
    acctsessionid = models.CharField(max_length=64)
    acctuniqueid = models.CharField(unique=True, max_length=32)
    username = models.CharField(max_length=64)
    groupname = models.CharField(max_length=64)
    realm = models.CharField(max_length=64, blank=True, null=True)
    nasipaddress = models.CharField(max_length=15)
    nasidentifier = models.CharField(max_length=64)
    nasportid = models.CharField(max_length=15, blank=True, null=True)
    nasporttype = models.CharField(max_length=32, blank=True, null=True)
    acctstarttime = models.DateTimeField(blank=True, null=True)
    acctupdatetime = models.DateTimeField(blank=True, null=True)
    acctstoptime = models.DateTimeField(blank=True, null=True)
    acctinterval = models.IntegerField(blank=True, null=True)
    acctsessiontime = models.PositiveIntegerField(blank=True, null=True)
    acctauthentic = models.CharField(max_length=32, blank=True, null=True)
    connectinfo_start = models.CharField(max_length=50, blank=True, null=True)
    connectinfo_stop = models.CharField(max_length=50, blank=True, null=True)
    acctinputoctets = models.BigIntegerField(blank=True, null=True)
    acctoutputoctets = models.BigIntegerField(blank=True, null=True)
    calledstationid = models.CharField(max_length=50)
    callingstationid = models.CharField(max_length=50)
    acctterminatecause = models.CharField(max_length=32)
    servicetype = models.CharField(max_length=32, blank=True, null=True)
    framedprotocol = models.CharField(max_length=32, blank=True, null=True)
    framedipaddress = models.CharField(max_length=15)
    # These fields have been added by radiusdesk
    acctstartdelay = models.IntegerField(blank=True, null=True)
    acctstopdelay = models.IntegerField(blank=True, null=True)
    xascendsessionsvrkey = models.CharField(max_length=20, blank=True, null=True)
    operator_name = models.CharField(max_length=32)

    class Meta:
        db_table = "radacct"

    def __str__(self):
        return f"Radacct for {self.username}: Connect at {self.nasidentifier} from {self.acctstarttime}-{self.acctstoptime}"


class Radcheck(models.Model):
    username = models.CharField(max_length=64)
    attribute = models.CharField(max_length=64)
    op = models.CharField(max_length=2)
    value = models.CharField(max_length=253)

    class Meta:
        db_table = "radcheck"

    def __str__(self):
        return f"Radcheck: {self.username}.{self.attribute} {self.op} {self.value}"


class Radgroupcheck(models.Model):
    groupname = models.CharField(max_length=64)
    attribute = models.CharField(max_length=64)
    op = models.CharField(max_length=2)
    value = models.CharField(max_length=253)
    # These fields have been added by radiusdesk
    comment = models.CharField(max_length=253)
    created = models.DateTimeField()
    modified = models.DateTimeField()

    class Meta:
        db_table = "radgroupcheck"

    def __str__(self):
        return (
            f"Radgroupcheck: {self.groupname}.{self.attribute} {self.op} {self.value}"
        )


class Radgroupreply(models.Model):
    groupname = models.CharField(max_length=64)
    attribute = models.CharField(max_length=64)
    op = models.CharField(max_length=2)
    value = models.CharField(max_length=253)
    # These fields have been added by radiusdesk
    comment = models.CharField(max_length=253)
    created = models.DateTimeField()
    modified = models.DateTimeField()

    class Meta:
        db_table = "radgroupreply"

    def __str__(self):
        return (
            f"Radgroupcheck: {self.groupname}.{self.attribute} {self.op} {self.value}"
        )


# This seems to be a model only used by radiusdesk?
class Radippool(models.Model):
    pool_name = models.CharField(max_length=30)
    framedipaddress = models.CharField(max_length=15)
    nasipaddress = models.CharField(max_length=15)
    calledstationid = models.CharField(max_length=30)
    callingstationid = models.CharField(max_length=30)
    expiry_time = models.DateTimeField(blank=True, null=True)
    username = models.CharField(max_length=64)
    pool_key = models.CharField(max_length=30)
    nasidentifier = models.CharField(max_length=64)
    extra_name = models.CharField(max_length=100)
    extra_value = models.CharField(max_length=100)
    active = models.IntegerField()
    permanent_user_id = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()

    class Meta:
        db_table = "radippool"

    def __str__(self):
        return f"Radippool: {self.pool_name}"


class Radpostauth(models.Model):
    username = models.CharField(max_length=64)
    realm = models.CharField(max_length=64, blank=True, null=True)
    pass_field = models.CharField(
        db_column="pass", max_length=64
    )  # Field renamed because it was a Python reserved word.
    reply = models.CharField(max_length=32)
    nasname = models.CharField(max_length=128)
    authdate = models.DateTimeField()

    class Meta:
        db_table = "radpostauth"

    def __str__(self):
        return f"Radpostauth: {self.username}@{self.realm} {self.pass_field} -> {self.reply}"


class Radreply(models.Model):
    username = models.CharField(max_length=64)
    attribute = models.CharField(max_length=64)
    op = models.CharField(max_length=2)
    value = models.CharField(max_length=253)

    class Meta:
        db_table = "radreply"

    def __str__(self):
        return f"Radreply: {self.username}.{self.attribute} {self.op} {self.value}"


class Radusergroup(models.Model):
    username = models.CharField(max_length=64)
    groupname = models.CharField(max_length=64)
    priority = models.IntegerField()

    class Meta:
        db_table = "radusergroup"

    def __str__(self):
        return (
            f"Radusergroup: {self.username}.{self.groupname} (priority={self.priority})"
        )


class Nas(models.Model):
    """A network Access Server (NAS).

    See https://wiki.freeradius.org/glossary/NAS
    """

    nasname = models.CharField(max_length=128)
    shortname = models.CharField(max_length=32, blank=True, null=True)
    nasidentifier = models.CharField(max_length=64)
    type = models.CharField(max_length=30, blank=True, null=True)
    ports = models.IntegerField(blank=True, null=True)
    secret = models.CharField(max_length=60)
    server = models.CharField(max_length=64, blank=True, null=True)
    community = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    # These are fields that radiusdesk has added
    connection_type = models.CharField(max_length=7, blank=True, null=True)
    timezone = models.CharField(max_length=255)
    record_auth = models.IntegerField()
    ignore_acct = models.IntegerField()
    dynamic_attribute = models.CharField(max_length=50)
    dynamic_value = models.CharField(max_length=50)
    monitor = models.CharField(max_length=9, blank=True, null=True)
    ping_interval = models.IntegerField()
    heartbeat_dead_after = models.IntegerField()
    last_contact = models.DateTimeField(blank=True, null=True)
    session_auto_close = models.IntegerField()
    session_dead_time = models.IntegerField()
    on_public_maps = models.IntegerField()
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    photo_file_name = models.CharField(max_length=128)
    cloud_id = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()

    class Meta:
        db_table = "nas"

    def __str__(self):
        return f"NAS {self.nasname}: type={self.type}"
