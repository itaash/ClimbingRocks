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

class ModelError(Error):
    """Raised when a model file could not be opened"""
    pass

class HoldModelError(Error):
    """Raised when a hold model file could not be opened"""
    pass
