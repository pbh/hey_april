hey_april
=========
April is a composable templating system.

__doc__
-------
April is a simple (read: extremely limited) composable template system.
It's honestly probably not any better than using a different templating
system, but it's a lot simpler.

April assumes you're going to use Bootstrap, and it comes with its own
Bootstrap bundled in package_data.  (You can use copy_assets to copy it
somewhere appropriate.)

Usually, you'll end up doing something like:

.. code:: python

 b_int1 = hey_april.BSSkeleton(
 'An Exciting Page Title',
 'Some Corner Text',
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
                 'txt/scores.csv'
                 )
             ]
         )
     ],
 'https://something.com'
 )
