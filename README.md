# NATS Event Handler Microservice Template

This templates provides the initial structure of
a Python-based microservice that allows subscribing
to a subject in NATS and it implements handling the 
matching events that have been published in NATS 
without coupling to the originator of the message. 
This microservice allows high decoupling between 
microservices that expose service interfaces and 
microservices that implement business logic. Since
this microservice also uses message queues by default
it support distributing workloads across multiple 
instances of this microservice.

## Maintainers
Pedro Guzmán (pedro.andres.guzman@ibm.com) @Pedro-Andres-Guzman
Roy Abarca (roy.abarca@ibm.com) @Roy-Abarca

## Getting Started

Provide an implementation of a class that Extends **AbstractNATSSubscriber**:

```python

from log_management.interfaces import MicroserviceLogger
from messaging import AbstractNATSSubscriber
import asyncio
import json


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
```

Now set the environment variables:

```bash
   % export NATS_SERVER='nats://localhost:4222'
   % export NATS_SUBJECT='test'
   % export NATS_QUEUE='workers'
```

Creat an entry point for the listener:

```python

from log_management.syslog_impl import SimpleLogger
import asyncio
import settings

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
```

Now run the subscriber locally:

```bash
    % virtualenv -p python3 venv
    % source venv/bin/activate
    % pip install -r requirements.txt
    % python listener.py
```