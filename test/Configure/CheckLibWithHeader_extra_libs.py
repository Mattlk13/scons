#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
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
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE

"""
Verify that a program which depends on library which in turn depends
on another library can be built correctly using CheckLibWithHeader
"""

from pathlib import Path

from TestSCons import TestSCons, dll_, _dll

test = TestSCons(match=TestSCons.match_re_dotall)

# This is the first library project
libA_dir = Path(test.workdir) / "libA"
libA_dir.mkdir()
libA = str(libA_dir / (dll_ + 'A' + _dll))  # for existence check
test.dir_fixture(['fixture', 'checklib_extra', 'libA'], 'libA')

# This is the second library project, depending on the first
libB_dir = Path(test.workdir) / "libB"
libB_dir.mkdir()
libB = str(libB_dir / (dll_ + 'B' + _dll))  # for existence check
test.dir_fixture(['fixture', 'checklib_extra', 'libB'], 'libB')

test.run(arguments='-C libA')
test.must_exist(libA)
test.run(arguments='-C libB')
test.must_exist(libB)

test.file_fixture(['fixture', 'checklib_extra', 'SConstruct'])
test.dir_fixture(['fixture', 'checklib_extra', 'src'], 'src')
test.run()

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
