#!/usr/bin/env python
#
# __COPYRIGHT__
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

"""
This tests the SRC bz2 packager, which does the following:
 - create a tar package from the specified files
"""

import TestSConsTar

test = TestSConsTar.TestSConsTar()

tar = test.detect('TAR', 'tar')
if not tar:
    test.skip_test('tar not found, skipping test\n')

is_wintar, is_bz2_supported = TestSConsTar.windows_system_tar_bz2(tar)
if is_wintar and not is_bz2_supported:
    test.skip_test('windows tar found; bz2 not supported, skipping test\n')

test.subdir('src')

test.write([ 'src', 'main.c'], r"""
int main( int argc, char* argv[] )
{
  return 0;
}
""")

test.write('SConstruct', """
Program( 'src/main.c' )
env=Environment(tools=['packaging', 'filesystem', 'tar'])

env.Package( PACKAGETYPE  = 'src_tarbz2',
             target       = 'src.tar.bz2',
             PACKAGEROOT  = 'test',
             source       = [ 'src/main.c', 'SConstruct' ] )
""")

test.run(arguments='', stderr=None)

test.must_exist('src.tar.bz2')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
