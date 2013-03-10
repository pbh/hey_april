#!/usr/bin/env python

import jinja2
import types
import os
import csv
import StringIO
import shutil

_ROOT = os.path.abspath(os.path.dirname(__file__))
_TEMPLATE_PATH = os.path.join(_ROOT, 'templates')
 
_template_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(_TEMPLATE_PATH))

_DEFAULT_ASSET_DEST_DIR = None
_DEFAULT_ASSET_OUTPUT_DIR_NAME = None
_DEFAULT_ASSET_PREFIX = None

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
    """
    HTMLable is the base class for pretty much everything in April.

    HTMLables can turn themselves into HTML (via to_html) and have 
    zero or more children.
    """
    def __init__(self):
        self._children = []

    def to_html(self):
        'Return an HTML version of this object (NotImplemented for base HTMLable).'
        raise NotImplementedError()

    def get_children(self):
        'Get children of this HTMLable.'
        return self._children

    def add_child(self, child):
        'Add a child HTMLable to this HTMLable.'
        self._children.append(child)

    def add_children(self, children):
        'Add zero or more HTMLable children to this HTMLable.'
        self._children.extend(children)

    def _get_possible_children(self, maybe_has_htmlables):
        'Utility for supporting list, tuple, or HTMLable for some methods.'
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
        'Utility for demanding a string (vs __str__ or __repr__).'
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
    """
    A base class for HTMLables that use the Bootstrap framework.

    The main difference vs HTMLable is that we assume that there will be
    zero or more navbar links.  Each BSHTMLable can produce its own navbar
    links and those of its children.
    """
    def __init__(self):
        super(BSHTMLable, self).__init__()

    def my_navbar_links(self):
        'What navbar links does this BSHTMLable want to add?'
        return []

    def get_navbar_links(self):
        'What are the navbar links of me and my children?'
        l = []
        
        for c in self.get_children():
            l.extend(c.get_navbar_links())

        l.extend(self.my_navbar_links())
        
        return l


class BSSkeleton(BSHTMLable):
    """
    A skeleton that contains the rest of a page.

    BSSkeleton is usually a top level container HTMLable that holds other
    HTMLables.  It loads assets, has a page title, head and corner, and has
    an HTMLable or list of HTMLables as its body.

    You can put assets wherever you want, so BSSkeleton allows you to specify
    an asset_prefix where assets will be searched for by the browser.
    (We don't check that this actually exists, we just put it into the
    template.)
    """
    def __init__(self, title, corner, head, body, asset_prefix=None, related=None):
        super(BSSkeleton, self).__init__()

        global _DEFAULT_ASSET_PREFIX

        self._title = title
        self._corner = corner
        self._head = head
        self._body = body
        self._asset_prefix = _DEFAULT_ASSET_PREFIX
        self._related = []

        if asset_prefix is not None:
            self._asset_prefix = asset_prefix

        if self._asset_prefix is None:
            raise RuntimeError(
                'Asset prefix cannot be None --- set a default or use manual.')
        
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
            asset_prefix=self._asset_prefix,
            related_pairs=self._related
            )


class BSHTML(BSHTMLable):
    'A simple pass-through, anything you pass will be directly added to the HTML.'
    def __init__(self, html):
        super(BSHTML, self).__init__()
        self._html = html

    def to_html(self):
        return self._html


class BSSection(BSHTMLable):
    """
    An HTMLable representing a section div.

    Sections have a title and subtitle which are both visible.
    They also have a name, used in navbar links.
    They have an anchor which is used in the navbar links but not shown.
    Lastly, a section can have zero or more child HTMLables representing
    the content of the section.
    """
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
    'A BSTwoUp shows two BSHTMLables side-by-side.'
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
    'A BSImg is a BSHTMLable for an HTML img tag.'
    def __init__(self, src, link=None, full_width=False, center_align=False):
        super(BSImg, self).__init__()
        self._src = src
        self._link = link
        self._full_width = full_width
        self._center_align = center_align

    def to_html(self):
        style_part = ''
        
        if self._full_width:
            style_part = 'style="width: 100%"'
        elif self._center_align:
            style_part = '''style="display: block; margin-left: auto; 
                            margin-right: auto"'''
      
        if self._link is not None:
            return '<a href="%s"><img src="%s" %s /></a>' % (
                self._link, self._src, style_part)
        else:
            return '<img src="%s" %s />' % (
                self._src, style_part)


class BSPara(BSHTMLable):
    'A BSPara is a BSHTMLable for an HTML p tag.'
    def __init__(self, sentences_str):
        super(BSPara, self).__init__()
        self._sentences_str = sentences_str

    def to_html(self):
        return '<p>%s</p>' % self._sentences_str


class BSCSVTable(BSHTMLable):
    'A BSCSVTable is an HTMLable that turns CSV output into an HTML table.'
    def __init__(self, fn_abs):
        super(BSCSVTable, self).__init__()
        self._fn_abs = fn_abs

    def to_html(self):
        return csv_to_bootstrap_table_html(file(self._fn_abs).read())


class BSPre(BSHTMLable):
    'A BSPre is a BSHTMLable for the HTML pre tag.'
    def __init__(self, preformatted_str):
        super(BSPre, self).__init__()
        self._preformatted_str = preformatted_str

    def to_html(self):
        return '<pre>%s</pre>' % self._preformatted_str


class BSSQLCode(BSHTMLable):
    'A BSSQLCode is a BSHTMLable that formats SQL code.'
    def __init__(self, sql_str):
        super(BSSQLCode, self).__init__()
        self._sql_str = sql_str

    def to_html(self):
        return '<pre class="prettyprint linenums lang-sql">%s</pre>' % self._sql_str

def set_default_asset_dest_dir(dest_dir):
    'Set the default destination to copy assets to.'
    global _DEFAULT_ASSET_DEST_DIR
    _DEFAULT_ASSET_DEST_DIR = dest_dir

def set_default_asset_output_dir_name(april_asset_dir_name):
    'Set the default name of the asset dir.'
    global _DEFAULT_ASSET_OUTPUT_DIR_NAME
    _DEFAULT_ASSET_OUTPUT_DIR_NAME = april_asset_dir_name

def set_default_asset_prefix(asset_prefix):
    'Set the default prefix for where to find assets.'
    global _DEFAULT_ASSET_PREFIX
    _DEFAULT_ASSET_PREFIX = asset_prefix

def copy_assets(dest_dir=None, april_asset_dir_name=None):
    """
    Copy the April assets to a directory.

    This function copies assets from the package_data of april to your destination
    directory dest_dir.  It will copy to one directory within dest_dir, which is
    specified as dest_dir/april_asset_dir_name.
    """

    global _DEFAULT_ASSET_DEST_DIR
    global _DEFAULT_ASSET_OUTPUT_DIR_NAME

    if dest_dir is None:
        dest_dir = _DEFAULT_ASSET_DEST_DIR

    if april_asset_dir_name is None:
        if _DEFAULT_ASSET_OUTPUT_DIR_NAME is not None:
            april_asset_dir_name = _DEFAULT_ASSET_OUTPUT_DIR_NAME
        else:
            april_asset_dir_name = 'april_assets'

    asset_dir = os.path.join(os.path.split(__file__)[0], 'assets')
    out_dir = os.path.join(dest_dir, april_asset_dir_name)

    shutil.copytree(asset_dir, out_dir)
