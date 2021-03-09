from log_management.syslog_impl import SimpleLogger
from log_management.interfaces import MicroserviceLogger
from messaging import AbstractNATSSubscriber
import asyncio
import json
import settings


# -----------------------------------------------------------------------------
# CLASS SAMPLE HANDLER
# -----------------------------------------------------------------------------
class SampleHandler(AbstractNATSSubscriber):

    # -------------------------------------------------------------------------
    # CLASS CONSTRUCTOR
    # -------------------------------------------------------------------------
    def __init__(self,
                 event_loop: asyncio.AbstractEventLoop,
                 logger: MicroserviceLogger,
                 subject: str,
                 queue: str
                 ):
        super().__init__(
            event_loop,
            logger,
            subject,
            queue
        )

    # -------------------------------------------------------------------------
    # METHOD MESSAGE HANDLER
    # -------------------------------------------------------------------------
    async def message_handler(self, message):
        self._logger.info(
            message.data.decode()
        )
        print(message.reply)
        await self.send_reply(
            json.dumps({"message": "This is a message response"}),
            message.reply
        )


if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    client = SampleHandler(
        event_loop=loop,
        logger=SimpleLogger(),
        subject=settings.NATS_SUBJECT,
        queue=settings.NATS_QUEUE
    )
    loop.run_until_complete(client.start())
    try:
        loop.run_forever()
    finally:
        loop.close()