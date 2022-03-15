class AuthRouter:
    """
    A router to control all database operations on models in the
    auth and contenttypes applications.
    """
    route_app_labels = {'blog', 'account', 'esi'}
    route_app_labels2 = {'eve'}

    def db_for_read(self, model, **hints):
        print("디비포리드")
        """
        Attempts to read auth and contenttypes models go to auth_db.
        """
        if model._meta.app_label in self.route_app_labels:
            print("ASASASASASASASASASASAS")
            return 'default'
        elif model._meta.app_label in self.route_app_labels2:
            print("ss")
            return 'eve'
        print(333333)
        return None

    def db_for_write(self, model, **hints):
        print("디비포라이트")
        """
        Attempts to write auth and contenttypes models go to auth_db.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'default'
        elif model._meta.app_label in self.route_app_labels2:
            return 'eve'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth or contenttypes apps is
        involved.
        """
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
           return True
        elif(
            obj1._meta.app_label in self.route_app_labels2 or
            obj2._meta.app_label in self.route_app_labels2
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth and contenttypes apps only appear in the
        'auth_db' database.
        """
        if app_label in self.route_app_labels:
            return db == 'default'
        elif app_label in self.route_app_labels2:
            return db == 'eve'
        return None