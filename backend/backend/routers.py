from django.conf import settings

class MetricsRouter:
    """
    A router to control database operations to the metrics database.
    """

    module_db_map = {
        "metrics": "metrics_db",
        # Allow radius data to be sourced either from the radiusdesk database
        # (if it is configured) or from the default database otherwise.
        "radius": ["radius_db", "default"]
    }

    def db_for_read(self, model, **hints):
        """
        Attempts to read metrics models from the metrics db.
        """
        db_name = self.module_db_map.get(model._meta.app_label)
        # If the db name is a list, pick the first db that has been configured in settings
        if isinstance(db_name, list):
            configured_dbs = [x for x in db_name if x in settings.DATABASES]
            return configured_dbs[0] if configured_dbs else "default"
        return db_name

    def db_for_write(self, model, **hints):
        """
        Attempts to write metrics models to the metrics db.
        """
        # Database for read is same as database for write
        return self.db_for_read(model, **hints)

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both objects are in the same db.
        """
        db1 = self.module_db_map.get(obj1._meta.app_label)
        db2 = self.module_db_map.get(obj2._meta.app_label)
        return db1 == db2

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure metrics tables only appear in the 'metrics_db' database.
        """
        db_name = self.module_db_map.get(app_label, "default")
        if isinstance(db_name, list):
            return db in db_name
        return db == db_name
