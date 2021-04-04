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

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, AnyStr


class AbstractSubject(ABC):
    """
    The events interface declares a set
    of methods for managing subscribers
    """

    @abstractmethod
    def generate(self, who: AnyStr, event: Any) -> dict:
        """ Generate an event as dict data """
        pass

    @abstractmethod
    def attach(self, observer: AbstractObserver) -> None:
        """ Attach an events instance """
        pass

    @abstractmethod
    def detach(self, observer: AbstractObserver) -> None:
        """ Detach an events instance """
        pass

    @abstractmethod
    def notify(self, event) -> None:
        """ Notify all events instances about an event """
        pass


class AbstractObserver(ABC):
    """
    The Observer declares the update
    method, used by subjects
    """

    @abstractmethod
    def update(self, event) -> None:
        """ Receive update from subject """
        pass
