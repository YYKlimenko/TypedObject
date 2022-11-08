import inspect
from types import FunctionType
from typing import Any

from loggers import logger


class TypedObjectMeta(type):

    @staticmethod
    def check_type(function):
        def wrapper(*args, **kwargs):
            count = 1
            for variable in function.__annotations__:
                if variable in locals()['kwargs']:
                    if type(locals()['kwargs'][variable]) != function.__annotations__[variable]:
                        raise TypeError(f'Type {variable} is not correct')
                else:
                    if type(locals()['args'][count]) != function.__annotations__[variable]:
                        raise TypeError(f'Type {variable} is not correct')
                    count += 1
            return function(*args, **kwargs)
        return wrapper

    @classmethod
    def _create_attrs(mcs, dct):
        methods = set()
        variables = dict()
        for _ in dct:
            if _ not in ['__module__', '__qualname__', '__annotations__']:
                if type(dct[_]) == FunctionType:
                    methods.add(dct[_])
                elif not isinstance(dct[_], type):
                    variables[_] = dct[_]
        return methods, variables

    @classmethod
    def _validate_methods(mcs, methods: set[FunctionType]) -> bool:
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
    def _validate_variables(mcs, dct, variables: dict[str, Any]) -> bool:
        if len(variables) == 0:
            return True
        for variable in variables:
            if dct.get('__annotations__') is None or variable not in dct['__annotations__'] or type(
                    variables[variable]) != dct['__annotations__'][variable]:
                raise TypeError(f'{variable} type is not correct')
        return True

    def __new__(mcs, name, bases, dct):
        if name != 'TypedObject':
            methods, variables = mcs._create_attrs(dct)
            if mcs._validate_methods(methods) and mcs._validate_variables(dct, variables):
                for method in methods:
                    dct[method.__name__] = TypedObjectMeta.check_type(method)
                return super().__new__(mcs, name, bases, dct)
        else:
            return super().__new__(mcs, name, bases, dct)
