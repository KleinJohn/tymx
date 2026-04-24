import types


class class_or_instance_method:
    """
    A custom decorator that binds the method to the class if called on the class,
    and binds it to the instance if called on the instance.
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        if instance is None:
            return types.MethodType(self.func, owner)
        return types.MethodType(self.func, instance)
