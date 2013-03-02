#!/usr/bin/env python

"""
    hey_april.*
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    SKEL

    :copyright: (c) 2013 by oDesk Corporation.
    :license: BSD, see LICENSE for more details.
"""

import jinja2
import types
import os
import csv
import StringIO

_ROOT = os.path.abspath(os.path.dirname(__file__))
_TEMPLATE_PATH = os.path.join(_ROOT, 'templates')
 
_template_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(_TEMPLATE_PATH))

def csv_to_bootstrap_table_html(csv_s_with_header):
    """
    Return the HTML of a table representing the CSV passed as a string.

    The CSV should have a header with names of the columns, and the HTML
    output includes classes for Twitter Bootstrap.

    Note that CSV is expected as a string, not as a file handle.
    """

    r = csv.DictReader(StringIO.StringIO(csv_s_with_header))
    
    template = _template_env.get_template('bootstrap_csv_table.html')

    return template.render(
        field_names = r.fieldnames,
        csv_lines = [line_d for line_d in r]
        )


class HTMLable(object):
    def __init__(self):
        self._children = []

    def to_html(self):
        raise NotImplementedError()

    def get_children(self):
        return self._children

    def add_child(self, child):
        self._children.append(child)

    def add_children(self, children):
        self._children.extend(children)

    def _get_possible_children(self, maybe_has_htmlables):
        if isinstance(maybe_has_htmlables, HTMLable):
            return [maybe_has_htmlables]
        elif (isinstance(maybe_has_htmlables, types.ListType) or 
              isinstance(maybe_has_htmlables, types.TupleType)):
            return [h for h in maybe_has_htmlables
                    if isinstance(h, HTMLable)]
        
        return []

    def _add_possible_children(self, maybe_has_htmlables):
        self.add_children(
            self._get_possible_children(maybe_has_htmlables))
 
    def _coerce_to_s(self, htmlable_string_or_list):
        if isinstance(htmlable_string_or_list, types.StringTypes):
            return htmlable_string_or_list
        
        elif isinstance(htmlable_string_or_list, HTMLable):
            return htmlable_string_or_list.to_html()

        elif (isinstance(htmlable_string_or_list, types.ListType) or 
              isinstance(htmlable_string_or_list, types.TupleType)):
            return ''.join(
                [self._coerce_to_s(subitem) for subitem in htmlable_string_or_list]
                )


class BSHTMLable(HTMLable):
    def __init__(self):
        super(BSHTMLable, self).__init__()

    def my_navbar_links(self):
        return []

    def get_navbar_links(self):
        l = []
        
        for c in self.get_children():
            l.extend(c.get_navbar_links())

        l.extend(self.my_navbar_links())
        
        return l


class BSSkeleton(BSHTMLable):
    def __init__(self, title, corner, head, body, related=None):
        super(BSSkeleton, self).__init__()

        self._title = title
        self._corner = corner
        self._head = head
        self._body = body
        self._related = []

        if related is not None:
            self._related = related

        self._add_possible_children(body)

    def to_html(self):
        template = _template_env.get_template('bootstrap_skel.html')

        navbar_id_name_pairs = [
            (k,v) for k,v in self.get_navbar_links()
            if (len(k) > 0) and (len(v) > 0)]

        return template.render(
            page_title=self._title,
            page_head=self._head,
            corner_name=self._corner,
            rest_of_body=self._coerce_to_s(self._body),
            navbar_id_name_pairs=navbar_id_name_pairs,
            related_pairs=self._related
            )


class BSHTML(BSHTMLable):
    def __init__(self, html):
        super(BSHTML, self).__init__()
        self._html = html

    def to_html(self):
        return self._html


class BSSection(BSHTMLable):
    def __init__(self, title, subtitle, name, html_id, children):
        super(BSSection, self).__init__()
        self._title = title
        self._subtitle = subtitle
        self._name = name
        self._id = html_id
        self._param_children = children
        self._add_possible_children(children)
        
    def my_navbar_links(self):
        return [(self._id, self._name)]

    def to_html(self):
        template = _template_env.get_template('bootstrap_section.html')

        return template.render(
            section_title=self._title,
            section_subtitle=self._subtitle,
            section_id=self._id,
            rest_of_section=self._coerce_to_s(self._param_children)
            )


class BSTwoUp(BSHTMLable):
    def __init__(self, left_children, right_children):
        super(BSTwoUp, self).__init__()
        self._left_children = left_children
        self._right_children = right_children

        self._add_possible_children(left_children)
        self._add_possible_children(right_children)

    def to_html(self):
        template = _template_env.get_template('bootstrap_twoup.html')

        return template.render(
            left_html=self._coerce_to_s(self._left_children),
            right_html=self._coerce_to_s(self._right_children)
            )


class BSImg(BSHTMLable):
    def __init__(self, src, link=None, full_width=False):
        super(BSImg, self).__init__()
        self._src = src
        self._link = link
        self._full_width = full_width

    def to_html(self):
        full_width_part = ''

        if self._full_width:
            full_width_part = "style='width: 100%'"

        if self._link is not None:
            return '<a href="%s"><img src="%s" %s /></a>' % (
                self._link, self._src, full_width_part)
        else:
            return '<img src="%s" %s />' % (
                self._src, full_width_part)


class BSPara(BSHTMLable):
    def __init__(self, sentences_str):
        super(BSPara, self).__init__()
        self._sentences_str = sentences_str

    def to_html(self):
        return '<p>%s</p>' % self._sentences_str


class BSCSVTable(BSHTMLable):
    def __init__(self, fn_abs):
        super(BSCSVTable, self).__init__()
        self._fn_abs = fn_abs

    def to_html(self):
        return csv_to_bootstrap_table_html(file(self._fn_abs).read())


class BSPre(BSHTMLable):
    def __init__(self, preformatted_str):
        super(BSPre, self).__init__()
        self._preformatted_str = preformatted_str

    def to_html(self):
        return '<pre>%s</pre>' % self._preformatted_str


class BSSQLCode(BSHTMLable):
    def __init__(self, sql_str):
        super(BSSQLCode, self).__init__()
        self._sql_str = sql_str

    def to_html(self):
        return '<pre class="prettyprint linenums lang-sql">%s</pre>' % self._sql_str

