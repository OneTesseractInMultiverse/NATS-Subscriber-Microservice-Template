from abc import abstractmethod, ABCMeta
from nats.aio.client import Client
from nats.aio.errors import ErrNoServers
from log_management.interfaces import MicroserviceLogger
from settings import NATS_SERVER
import asyncio
import signal


# -----------------------------------------------------------------------------
# CLASS ABSTRACT NATS SUBSCRIBER
# -----------------------------------------------------------------------------
class AbstractNATSSubscriber(object):

    """
    This class is meant to be extended by classes that need to provide a concrete
    implementation of an Event Subscriber that will subscribe to a set of particular
    events
    """

    __metaclass__ = ABCMeta

    # -------------------------------------------------------------------------
    # CLASS CONSTRUCTOR
    # -------------------------------------------------------------------------
    def __init__(self,
                 event_loop: asyncio.AbstractEventLoop,
                 logger: MicroserviceLogger,
                 subject: str,
                 queue: str):
        """
        Creates instances of NATS Subscriber
        :param event_loop: The asyncio event loop
        :param logger: Implementation of MicroserviceLogger
        :param subject: Subject that this listener is going to subscribe
        :param queue: Queue for this listener
        """
        self._nats_client = Client()
        self._loop = event_loop
        self._logger: MicroserviceLogger = logger
        self.subject: str = subject
        self.queue: str = queue
        self._options = {
            "loop": self._loop,
            "error_cb": self._error_event_handler,
            "closed_cb": self._connection_closed_event_handler,
            "reconnected_cb": self._reconnect_event_handler
        }

    # -------------------------------------------------------------------------
    # METHOD REGISTER SIGNAL HANDLERS
    # -------------------------------------------------------------------------
    def _register_signal_handlers(self):
        """

        :return:
        """
        for signal_name in ('SIGINT', 'SIGTERM'):
            self._loop.add_signal_handler(
                getattr(signal, signal_name),
                self._signal_handler
            )

    # -------------------------------------------------------------------------
    # METHOD SIGNAL HANDLER METHOD
    # -------------------------------------------------------------------------
    def _signal_handler(self):
        """

        :return:
        """
        if self._nats_client.is_closed:
            return
        self._logger.info("Disconnecting from NATS server...")
        self._loop.create_task(self._nats_client.close())

    # -------------------------------------------------------------------------
    # METHOD CONNECT
    # -------------------------------------------------------------------------
    async def _connect(self):
        """
        Opens a connection to NATS messaging cluster and registers the local
        signal handlers that allow process shutdown when a signal is received
        from the OS

        :return: True if connection was successful, False if the connection
                 failed
        """
        try:
            await self._nats_client.connect(
                servers=NATS_SERVER.split(',')
            )
            self._register_signal_handlers()
            return True
        except ErrNoServers as ens:
            self._logger.error(message=str(ens))
        except Exception as e:
            self._logger.error(message=str(e))
        return False

    # -------------------------------------------------------------------------
    # ERROR EVENT HANDLER
    # -------------------------------------------------------------------------
    async def _error_event_handler(self, event):
        """

        :param event:
        :return:
        """
        self._logger.error(f"NATS Error: \n {event}")

    # -------------------------------------------------------------------------
    # CONNECTION CLOSED EVENT HANDLER
    # -------------------------------------------------------------------------
    async def _connection_closed_event_handler(self):
        """

        :return:
        """
        self._logger.info(f"Connection to NATS cluster is closed")
        await asyncio.sleep(0.1, loop=self._loop)
        self._loop.stop()

    # -------------------------------------------------------------------------
    # METHOD RECONNECT EVENT HANDLER
    # -------------------------------------------------------------------------
    async def _reconnect_event_handler(self):
        """

        :return:
        """
        self._logger.info(
            f"Connected to NATS cluster at: {self._nats_client.connected_url.netloc}"
        )

    # -------------------------------------------------------------------------
    # METHOD START
    # -------------------------------------------------------------------------
    async def start(self):
        """

        :return:
        """
        if await self._connect():
            self._logger.info(
                f'Connection to NATS cluster was successful. Subscribing to {self.subject}'
            )
            self._logger.info(
                f'Using queue: {self.queue}'
            )
            await self._nats_client.subscribe(
                self.subject,
                self.queue,
                self.message_handler
            )
        else:
            self._logger.error(
                f'Unable to connect to NATS servers at: {NATS_SERVER.split(",")}'
            )

    # -------------------------------------------------------------------------
    # METHOD SEND REPLY
    # -------------------------------------------------------------------------
    async def send_reply(self, message: str, subject: str):
        try:
            await self._nats_client.publish(
                subject,
                message.encode()
            )
        except asyncio.TimeoutError as te:
            self._logger.error(str(te))
            raise te
        except Exception as e:
            self._logger.error(str(e))
            raise e

    # -------------------------------------------------------------------------
    # METHOD MESSAGE HANDLER
    # -------------------------------------------------------------------------
    @abstractmethod
    async def message_handler(self, message):
        """
        This method needs to be implemented by any class that extends this class
        :param message: The message that came from the subscribed channel
        :return:
        """
        pass
