import inspect

from types import FunctionType
from typing import Any


class TypedObjectMeta(type):

    @staticmethod
    def check_type(function):
        """The function to checking attributes types and type of return value. It's a decorator"""

        def wrapper(*args, **kwargs):
            return_type = inspect.signature(function).return_annotation
            signature = inspect.signature(function)
            parameters = dict(signature.parameters)
            parameters.pop('self')

            count = 1
            for parameter in parameters:

                try:
                    if parameter in kwargs:
                        if type(kwargs[parameter]) == parameters[parameter].annotation:
                            continue
                    elif type(args[count]) == parameters[parameter].annotation:
                        count += 1
                        continue
                except IndexError:
                    if type(parameters[parameter].default) == parameters[parameter].annotation:
                        continue
                raise TypeError(f'Type {parameter} is not correct')

            result = function(*args, **kwargs)
            if (return_type, result) == (None, None) or return_type == type(result):
                return result

        return wrapper

    @classmethod
    def _create_attrs(mcs, dct):
        """The function create lists of methods and static variables in Class"""

        methods, variables = set(), dict()
        for _ in dct:
            if _ not in ['__module__', '__qualname__', '__annotations__']:
                if type(dct[_]) == FunctionType:
                    methods.add(dct[_])
                elif not isinstance(dct[_], type):
                    variables[_] = dct[_]
        return methods, variables

    @classmethod
    def is_methods_validate(mcs, methods: set[FunctionType]) -> bool:
        """The function to checking annotations in methods"""

        for method in methods:
            attrs = set(inspect.signature(method).parameters)
            annotations = method.__annotations__
            for attr in attrs:
                if attr not in annotations and attr != 'self':
                    raise TypeError(
                        f'Attribute \'{attr}\' in method \'{method.__name__}\' '
                        f'doesn\'t have an type annotation'
                        )
        return True

    @classmethod
    def is_variables_validate(mcs, dct, variables: dict[str, Any]) -> bool:
        """The function to checking static variables annotations"""

        if len(variables) != 0:
            for variable in variables:
                if dct.get(
                        '__annotations__'
                ) is None or variable not in dct['__annotations__'] or type(
                        variables[variable]) != dct['__annotations__'][variable]:
                    raise TypeError(f'{variable} type is not correct')
        return True

    def __new__(mcs, name, bases, dct):
        """The function to checking annotations and decorating function by check_type"""

        cls = super().__new__(mcs, name, bases, dct)
        methods, variables = mcs._create_attrs(dct)
        if mcs.is_methods_validate(methods) and mcs.is_variables_validate(dct, variables):
            for method in methods:
                setattr(cls, method.__name__, TypedObjectMeta.check_type(method))
        return cls
