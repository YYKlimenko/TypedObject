def check_type(function):
    def wrapper(*args, **kwargs):
        count = 0
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
