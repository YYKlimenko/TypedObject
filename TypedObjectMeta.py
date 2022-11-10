import inspect
import shelve
from types import FunctionType
from typing import Any

import loggers


class TypedObjectMeta(type):

    @staticmethod
    def check_type(function):
        def wrapper(*args, **kwargs):
            return_type = None
            count = 1
            for variable in function.__annotations__:
                if variable == 'return':
                    return_type = function.__annotations__[variable]
                    continue
                if variable in locals()['kwargs']:
                    if type(locals()['kwargs'][variable]) != function.__annotations__[variable]:
                        raise TypeError(f'Type {variable} is not correct')
                else:
                    if type(locals()['args'][count]) != function.__annotations__[variable]:
                        raise TypeError(f'Type {variable} is not correct')
                    count += 1
            result = function(*args, **kwargs)
            if result is None:
                result_type = result
            else:
                result_type = type(result)
            if result_type == return_type:
                return result
            raise TypeError(f'The function return incorrect typed value')
        return wrapper

    @classmethod
    def _create_attrs(mcs, dct):
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
        if len(variables) != 0:
            for variable in variables:
                if dct.get(
                        '__annotations__'
                ) is None or variable not in dct['__annotations__'] or type(
                        variables[variable]) != dct['__annotations__'][variable]:
                    raise TypeError(f'{variable} type is not correct')
        return True

    def __new__(mcs, name, bases, dct):
        cls = super().__new__(mcs, name, bases, dct)
        if name != 'TypedObject':
            types = shelve.open(f'{name}')
            source = inspect.getsource(cls)
            methods, variables = mcs._create_attrs(dct)
            if types.get('source') != source:
                loggers.logger.debug(f'{cls.__name__}')
                if mcs.is_methods_validate(methods) and mcs.is_variables_validate(dct, variables):
                    types['source'] = source
            for method in methods:
                setattr(cls, method.__name__, TypedObjectMeta.check_type(method))
        return cls
