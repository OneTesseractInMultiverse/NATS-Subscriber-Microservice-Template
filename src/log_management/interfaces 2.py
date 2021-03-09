from abc import ABCMeta, abstractmethod
import enum


# -----------------------------------------------------------------------------
# CLASS LOG LEVEL
# -----------------------------------------------------------------------------
class LogLevel(enum.Enum):

    INFO = 0
    WARNING = 1
    ERROR = 2
    DEBUG = 3


# -----------------------------------------------------------------------------
# CLASS LOGGER BASE
# -----------------------------------------------------------------------------
class MicroserviceLogger(object):

    __metaclass__ = ABCMeta

    """
    A simple logger interface that provides abstraction of the actual 
    implementation of the logger and enables injecting loggers to classes
    through dependency inversion principle. 
    """

    @abstractmethod
    def debug(self, message: str, **kwargs) -> dict:
        pass

    @abstractmethod
    def info(self, message: str, **kwargs) -> dict:
        pass

    @abstractmethod
    def warning(self, message: str, **kwargs) -> dict:
        pass

    @abstractmethod
    def error(self, message: str, **kwargs) -> dict:
        pass