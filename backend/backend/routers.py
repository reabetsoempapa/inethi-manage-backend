class MetricsRouter:
    """
    A router to control database operations to the metrics database.
    """

    module_db_map = {
        "metrics": "metrics_db"
    }

    def db_for_read(self, model, **hints):
        """
        Attempts to read metrics models from the metrics db.
        """
        return self.module_db_map.get(model._meta.app_label)

    def db_for_write(self, model, **hints):
        """
        Attempts to write metrics models to the metrics db.
        """
        return self.module_db_map.get(model._meta.app_label)

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
        return db == self.module_db_map.get(app_label, "default")
