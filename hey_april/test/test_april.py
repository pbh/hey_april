import unittest2
import hey_dl
import hey_april
import warnings
import os

from bs4 import BeautifulSoup

warnings.filterwarnings("ignore", "tempnam", RuntimeWarning)
warnings.filterwarnings("ignore", "tmpnam", RuntimeWarning)

class AprilTestCase(unittest2.TestCase):
    def setUp(self):
        self._dl = hey_dl.DirectoryLocalizer()
        self._dl.set()

    def tearDown(self):
        pass

    def test_blank_skel(self):
        bskel = hey_april.BSSkeleton('my title', 'some text', '', '', 'https://test.test')

        soup = BeautifulSoup(bskel.to_html())

        self.assertEqual(len(soup.select('.navbar')), 1)
        self.assertEqual(soup.title.string, 'my title')

    def test_skel_assets(self):
        bskel = hey_april.BSSkeleton('my title', 'some text', '', '', 'https://test.test')
        skel_html = bskel.to_html()

        soup = BeautifulSoup(skel_html)
        self.assertTrue(
            soup.select('link')[0]['href'].startswith('https://test.test/'))

    def test_html_passthru(self):
        b1 = hey_april.BSHTML('foo')
        b2 = hey_april.BSHTML('<div>bar</div>')

        self.assertEqual(b1.to_html(), 'foo')
        self.assertEqual(b2.to_html(), '<div>bar</div>')

    def test_coerce_string(self):
        h = hey_april.HTMLable()

        self.assertEqual('foo', h._coerce_to_s('foo'))

    def test_coerce_htmlable(self):
        h = hey_april.HTMLable()

        self.assertEqual('foo', h._coerce_to_s(hey_april.BSHTML('foo')))
        
    def test_coerce_array(self):
        h = hey_april.HTMLable()

        self.assertEqual('foo', h._coerce_to_s([hey_april.BSHTML('foo')]))
        self.assertEqual('bar', h._coerce_to_s(['bar']))
        self.assertEqual('foobar', h._coerce_to_s([hey_april.BSHTML('foo'), 'bar']))

    def test_section_html(self):
        b1 = hey_april.BSSection('foo', 'bar', 'foo', 'foo', 
                                  [hey_april.BSHTML("<p class='what'>snooze</p>")])

        soup = BeautifulSoup(b1.to_html())

        self.assertEqual(len(soup.select('.what')), 1)
        self.assertEqual(len(soup('section')), 1)

    def test_twoup_html(self):
        b1 = hey_april.BSTwoUp([], [])
        soup = BeautifulSoup(b1.to_html())

        self.assertEqual(len(soup.select('.row')), 1)

    def test_img_html1(self):
        b1 = hey_april.BSImg('foo.jpg')

        soup = BeautifulSoup(b1.to_html())
        
        self.assertEqual(len(soup.select('img')), 1)
        self.assertEqual(len(soup.select('a')), 0)
        
    def test_img_html2(self):
        b1 = hey_april.BSImg('foo.jpg', 'foo.R')

        soup = BeautifulSoup(b1.to_html())
        
        self.assertEqual(len(soup.select('img')), 1)
        self.assertEqual(len(soup.select('a')), 1)

    def test_para_html(self):
        b1 = hey_april.BSPara('something')
        soup = BeautifulSoup(b1.to_html())

        self.assertEqual(len(soup.select('p')), 1)
        self.assertEqual(soup.select('p')[0].string, 'something')

    def test_csv_table_html(self):
        b1 = hey_april.BSCSVTable(self._dl.path('txt/scores.csv'))
        soup = BeautifulSoup(b1.to_html())

        self.assertEqual(len(soup.select('tr')), 5)
        self.assertEqual(len(soup.select('thead')), 1)
        
    def test_pre_html(self):
        b1 = hey_april.BSPre('something')
        soup = BeautifulSoup(b1.to_html())

        self.assertEqual(len(soup.select('pre')), 1)
        self.assertEqual(soup.select('pre')[0].string, 'something')
        self.assertEqual(len(soup.select('.lang-sql')), 0)
        
    def test_sql_html(self):
        b1 = hey_april.BSSQLCode('something')
        soup = BeautifulSoup(b1.to_html())

        self.assertEqual(len(soup.select('pre')), 1)
        self.assertEqual(soup.select('pre')[0].string, 'something')
        self.assertEqual(len(soup.select('.lang-sql')), 1)

    def test_integration1(self):
        b_int1 = hey_april.BSSkeleton(
            'Integration 1',
            'Integration',
            '',
            [
                hey_april.BSSection(
                    'Section 1', 'The second section...', 'Section 1', 'sec1',
                    [
                        hey_april.BSPara('this is the first section')
                        ]
                    ),
                hey_april.BSSection(
                    'Section 2', 'Another section!', 'Section 2', 'sec2',
                    [
                        hey_april.BSTwoUp(
                            hey_april.BSHTML('foo'),
                            hey_april.BSHTML('bar')
                            )
                        ]
                    ),
                hey_april.BSSection(
                    'Section 3', 'The CSV!', 'Section 3', 'sec3',
                    [
                        hey_april.BSCSVTable(
                            self._dl.path('txt/scores.csv')
                            )
                        ]
                    )
                ],
            'https://test.test'
            )

        soup = BeautifulSoup(b_int1.to_html())

        self.assertEqual(len(soup.select('section')), 3) # we're expecting 3 sections
        self.assertEqual(len(soup.select('tr')), 5)
        self.assertEqual(len(soup.select('li')), 4) # we're expecting 4 navbar entries

    def test_copy_assets(self):
        out_dir = os.tempnam('/tmp/')
        hey_april.copy_assets(out_dir, 'assets')

        self.assertTrue(
            os.path.isfile(
                os.path.join(out_dir, 'assets', 'bootstrap-2.2.2',
                             'css', 'bootstrap.css')))

