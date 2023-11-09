# define Python user-defined exceptions
class Error(Exception):
    """Base class for other exceptions"""
    pass


class CameraNotFoundError(Error):
    """Raised when a camera is not detected"""
    pass


class FontError(Error):
    """Raised when a font file could not be opened"""
    pass
