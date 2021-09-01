# -*- coding: utf-8 -*-
'''
Created on 2018-10-08 15:33:37
---------
@summary: 重新定义 selector
---------
@author:
@email:
'''
import re

import six
from parsel import Selector as ParselSelector
from parsel import SelectorList as ParselSelectorList
from w3lib.html import replace_entities as w3lib_replace_entities


def extract_regex(regex, text, replace_entities=True, flags=0):
    """Extract a list of unicode strings from the given text/encoding using the following policies:
    * if the regex contains a named group called "extract" that will be returned
    * if the regex contains multiple numbered groups, all those will be returned (flattened)
    * if the regex doesn't contain any group the entire regex matching is returned
    """
    if isinstance(regex, six.string_types):
        regex = re.compile(regex, flags=flags)

    if 'extract' in regex.groupindex:
        # named group
        try:
            extracted = regex.search(text).group('extract')
        except AttributeError:
            strings = []
        else:
            strings = [extracted] if extracted is not None else []
    else:
        # full regex or numbered groups
        strings = regex.findall(text)

    # strings = flatten(strings) # 这东西会把多维列表铺平
    if not replace_entities:
        return strings

    values = []
    for value in strings:
        if isinstance(value, (list, tuple)):  # w3lib_replace_entities 不能接收list tuple
            values.append([w3lib_replace_entities(v, keep=['lt', 'amp']) for v in value])
        else:
            values.append(w3lib_replace_entities(value, keep=['lt', 'amp']))

    return values


class SelectorList(ParselSelectorList):
    """
    The :class:`SelectorList` class is a subclass of the builtin ``list``
    class, which provides a few additional methods.
    """

    def re_first(self, regex, default=None, replace_entities=True, flags=re.S):
        """
        Call the ``.re()`` method for the first element in this list and
        return the result in an unicode string. If the list is empty or the
        regex doesn't match anything, return the default value (``None`` if
        the argument is not provided).

        By default, character entity references are replaced by their
        corresponding character (except for ``&amp;`` and ``&lt;``.
        Passing ``replace_entities`` as ``False`` switches off these
        replacements.
        """

        datas = self.re(regex, replace_entities=replace_entities, flags=flags)
        return datas[0] if datas else default

    def re(self, regex, replace_entities=True, flags=re.S):
        """
        Call the ``.re()`` method for each element in this list and return
        their results flattened, as a list of unicode strings.

        By default, character entity references are replaced by their
        corresponding character (except for ``&amp;`` and ``&lt;``.
        Passing ``replace_entities`` as ``False`` switches off these
        replacements.
        """
        datas = [x.re(regex, replace_entities=replace_entities, flags=flags) for x in self]
        return datas[0] if len(datas) == 1 else datas


class Selector(ParselSelector):
    selectorlist_cls = SelectorList

    def __str__(self):
        data = repr(self.get())
        return "<%s xpath=%r data=%s>" % (type(self).__name__, self._expr, data)

    __repr__ = __str__

    def re_first(self, regex, default=None, replace_entities=True, flags=re.S):
        """
        Apply the given regex and return the first unicode string which
        matches. If there is no match, return the default value (``None`` if
        the argument is not provided).

        By default, character entity references are replaced by their
        corresponding character (except for ``&amp;`` and ``&lt;``.
        Passing ``replace_entities`` as ``False`` switches off these
        replacements.
        """

        datas = self.re(regex, replace_entities=replace_entities, flags=flags)

        return datas[0] if datas else default

    def re(self, regex, replace_entities=True, flags=re.S):
        """
        Apply the given regex and return a list of unicode strings with the
        matches.

        ``regex`` can be either a compiled regular expression or a string which
        will be compiled to a regular expression using ``re.compile(regex)``.

        By default, character entity references are replaced by their
        corresponding character (except for ``&amp;`` and ``&lt;``.
        Passing ``replace_entities`` as ``False`` switches off these
        replacements.
        """

        return extract_regex(regex, self.get(), replace_entities=replace_entities, flags=flags)
