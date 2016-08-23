class SimpleKitError(Exception):
    pass


class MailException(SimpleKitError):
    pass


class GeneralError(SimpleKitError):
    """

    """


class ContainerNotFound(SimpleKitError):
    """Container Not Found Exception

    """


class ImageNotFound(SimpleKitError):
    """Image Not Found

    """


class ImageConflict(SimpleKitError):
    """Image Conflict

    """
