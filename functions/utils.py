# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License

# for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.
#
# Author: Jeffersson Abreu (ctw6av)

import re


def to_int(obj: str):
    """
    Convet a string to integer if possible
    and if not possible make it lowercase
    :param obj: Any string digit
    :return: Undefined
    """
    if obj.isdigit():
        return int(obj)
    return obj.lower()


def order_by_alphanum(item, keyword=None) -> list:
    """
    Return a list of ordered by alphanumeric string. By
    passing a keyword to sort and if no keyword is given
    the primary key in dicts elements will be used to sort

    :param item: The item can be a alphanumeric string or a dict
    :param keyword: In case of item is a dict the we can set a key to sort
    :return: Sorted in alphanumeric list
    """

    if isinstance(item, str):
        # If the item is a string we extract the integers and
        # convert it to the real type (int) to help sorting
        return [to_int(c) for c in re.split('([0-9]+)', item)]

    if isinstance(item, dict):
        # If the item is a dict we extract and no keyword was
        # given we try to get the first key value to sort.
        if keyword is None:
            keys = list(item.keys())
            keyword = keys[0]

        # Otherwise the dict key value gonna be used to sort
        return [to_int(c) for c in re.split('([0-9]+)', str(item[keyword]))]


def natural_sort(_list: list, keyword=None) -> list:
    """
    Sort a list by natural keys. This functions can also
    sort a list of dict by passing a keyword to sort and
    if no keyword is given the primary key in dicts elements
    will be used to sort

    :param _list: A list containing string elements or dicts
    :param keyword: A key of dict if the list elements are dicts
    :return: A list sorted.
    """
    return sorted(_list, key=lambda key: order_by_alphanum(key, keyword=keyword))
