class BaseException(Exception):
    """Base exception class"""
    
    def __init__(self, msg: str = 'Error'):
        super().__init__(msg)

    def __str__(self):
        base_message = super().__str__()
        return base_message


class UserAlreadyExist(BaseException):
    def __init__(self, msg: str='User with such user_id already exists'):
        super().__init__(msg)

class UserNotExist(BaseException):
    def __init__(self, msg: str='User with such user_id does not exist'):
        super().__init__(msg)

class NoDBConnectionError(BaseException):
    def __init__(self, msg: str='No database connection'):
        super().__init__(msg)
