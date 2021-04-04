# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.
#
# Author: Jeffersson Abreu (ctw6av)

import queue
from typing import List, AnyStr, Any
from threading import Thread
from events.bases import (
    AbstractObserver,
    AbstractSubject
)


class Subject(AbstractSubject):
    """
    All classes that inherits of this class should
    be able to notify all observers about a subject
    """
    def __init__(self, *args, **kwargs):

        # Keep a list of all observers
        self._observers: List[AbstractObserver] = []

    def generate(self, who: AnyStr, event: Any) -> dict:
        """ Generate an event as dict data """
        return {
            'who': who,
            'event': event
        }

    def attach(self, observer: AbstractObserver) -> None:
        """ Attach an events to observers list """
        self._observers.append(observer)

    def detach(self, observer: AbstractObserver) -> None:
        """ Detach an events from observers list """
        self._observers.remove(observer)

    def notify(self, data) -> None:
        """ Notify all observers """
        event = self.generate(
            who=self.__class__.__name__,
            event=data
        )
        for observer in self._observers:
            observer.update(event)


class Observer(AbstractObserver, Subject, Thread):
    """
    The Observer is attached to subjects
    and are notified when events occurs
    """

    def __init__(self, *args, **kwargs):
        Thread.__init__(self, *args, **kwargs)
        Subject.__init__(self, *args, **kwargs)

        # Run as a daemon
        self.daemon = True

        # Keep a list of events
        self.queue = queue.Queue()

        # Starts it self
        self.start()

    def update(self, event) -> None:
        """ Put all events in a queue """
        self.queue.put(event)

    def run(self) -> None:
        raise NotImplementedError


__all__ = [
    'Observer',
    'Subject'
]
