# Copyright 2000-2010 Steven Knight
#
# This module is free software, and you may redistribute it and/or modify
# it under the same terms as Python itself, so long as this copyright message
# and disclaimer are retained in their original form.
#
# IN NO EVENT SHALL THE AUTHOR BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT,
# SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OF
# THIS CODE, EVEN IF THE AUTHOR HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.
#
# THE AUTHOR SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE.  THE CODE PROVIDED HEREUNDER IS ON AN "AS IS" BASIS,
# AND THERE IS NO OBLIGATION WHATSOEVER TO PROVIDE MAINTENANCE,
# SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
#
# Python License: https://docs.python.org/3/license.html#psf-license

"""
A testing framework for commands and scripts with commonly useful error handling

The TestCommon module provides a simple, high-level interface for writing
tests of executable commands and scripts, especially commands and scripts
that interact with the file system.  All methods throw exceptions and
exit on failure, with useful error messages.  This makes a number of
explicit checks unnecessary, making the test scripts themselves simpler
to write and easier to read.

The TestCommon class is a subclass of the TestCmd class.  In essence,
TestCommon is a wrapper that handles common TestCmd error conditions in
useful ways.  You can use TestCommon directly, or subclass it for your
program and add additional (or override) methods to tailor it to your
program's specific needs.  Alternatively, the TestCommon class serves
as a useful example of how to define your own TestCmd subclass.

As a subclass of TestCmd, TestCommon provides access to all of the
variables and methods from the TestCmd module.  Consequently, you can
use any variable or method documented in the TestCmd module without
having to explicitly import TestCmd.

A TestCommon environment object is created via the usual invocation:

    import TestCommon
    test = TestCommon.TestCommon()

You can use all of the TestCmd keyword arguments when instantiating a
TestCommon object; see the TestCmd documentation for details.

Here is an overview of the methods and keyword arguments that are
provided by the TestCommon class:

    test.must_be_writable('file1', ['file2', ...])

    test.must_contain('file', 'required text\n')

    test.must_contain_all(output, input, ['title', find])

    test.must_contain_all_lines(output, lines, ['title', find])

    test.must_contain_single_instance_of(output, lines, ['title'])

    test.must_contain_any_line(output, lines, ['title', find])

    test.must_contain_exactly_lines(output, lines, ['title', find])

    test.must_exist('file1', ['file2', ...], ['message'])

    test.must_exist_one_of(files, ['message'])

    test.must_match('file', "expected contents\n")

    test.must_match_file(file, golden_file, ['message', 'newline'])

    test.must_not_be_writable('file1', ['file2', ...])

    test.must_not_contain('file', 'banned text\n')

    test.must_not_contain_any_line(output, lines, ['title', find])

    test.must_not_contain_lines(lines, output, ['title', find]):

    test.must_not_exist('file1', ['file2', ...])

    test.must_not_exist_any_of(files)

    test.must_not_be_empty('file')

    test.run(
        options="options to be prepended to arguments",
        arguments="string or list of arguments",
        stdout="expected standard output from the program",
        stderr="expected error output from the program",
        status=expected_status,
        match=match_function,
    )

The TestCommon module also provides the following variables

    TestCommon.python
    TestCommon._python_
    TestCommon.exe_suffix
    TestCommon.obj_suffix
    TestCommon.shobj_prefix
    TestCommon.shobj_suffix
    TestCommon.lib_prefix
    TestCommon.lib_suffix
    TestCommon.dll_prefix
    TestCommon.dll_suffix

"""

from __future__ import annotations

__author__ = "Steven Knight <knight at baldmt dot com>"
__revision__ = "TestCommon.py 1.3.D001 2010/06/03 12:58:27 knight"
__version__ = "1.3"

import glob
import os
import stat
import sys
import sysconfig

from collections import UserList
from typing import Callable

from TestCmd import *
from TestCmd import __all__

__all__.extend(
    [
        'TestCommon',
        'exe_suffix',
        'obj_suffix',
        'shobj_prefix',
        'shobj_suffix',
        'lib_prefix',
        'lib_suffix',
        'dll_prefix',
        'dll_suffix',
    ]
)

# Variables that describe the prefixes and suffixes on this system.
if sys.platform == 'win32':
    if sysconfig.get_platform() == "mingw":
        obj_suffix = '.o'
        shobj_suffix = '.o'
    else:
        obj_suffix = '.obj'
        shobj_suffix = '.obj'
    exe_suffix = '.exe'
    shobj_prefix = ''
    lib_prefix = ''
    # TODO: for mingw, is this .lib or .a?
    lib_suffix = '.lib'
    dll_prefix = ''
    dll_suffix = '.dll'
elif sys.platform == 'cygwin':
    exe_suffix = '.exe'
    obj_suffix = '.o'
    shobj_suffix = '.os'
    shobj_prefix = ''
    lib_prefix = 'lib'
    lib_suffix = '.a'
    dll_prefix = 'cyg'
    dll_suffix = '.dll'
elif sys.platform.find('irix') != -1:
    exe_suffix = ''
    obj_suffix = '.o'
    shobj_suffix = '.o'
    shobj_prefix = ''
    lib_prefix = 'lib'
    lib_suffix = '.a'
    dll_prefix = 'lib'
    dll_suffix = '.so'
elif sys.platform.find('darwin') != -1:
    exe_suffix = ''
    obj_suffix = '.o'
    shobj_suffix = '.os'
    shobj_prefix = ''
    lib_prefix = 'lib'
    lib_suffix = '.a'
    dll_prefix = 'lib'
    dll_suffix = '.dylib'
elif sys.platform.find('sunos') != -1:
    exe_suffix = ''
    obj_suffix = '.o'
    shobj_suffix = '.pic.o'
    shobj_prefix = ''
    lib_prefix = 'lib'
    lib_suffix = '.a'
    dll_prefix = 'lib'
    dll_suffix = '.so'
else:
    exe_suffix = ''
    obj_suffix = '.o'
    shobj_suffix = '.os'
    shobj_prefix = ''
    lib_prefix = 'lib'
    lib_suffix = '.a'
    dll_prefix = 'lib'
    dll_suffix = '.so'


def is_List(e):
    return isinstance(e, (list, UserList))


def is_Tuple(e):
    return isinstance(e, tuple)


def is_Sequence(e):
    return (
        not hasattr(e, "strip") and hasattr(e, "__getitem__") or hasattr(e, "__iter__")
    )


def is_writable(f):
    mode = os.stat(f).st_mode
    return mode & stat.S_IWUSR


def separate_files(flist):
    existing = []
    missing = []
    for f in flist:
        if os.path.exists(f):
            existing.append(f)
        else:
            missing.append(f)
    return existing, missing


def contains(seq, subseq, find: Callable | None = None) -> bool:
    if find is None:
        return subseq in seq
    else:
        f = find(seq, subseq)
        return f not in (None, -1) and f is not False


def find_index(seq, subseq, find: Callable | None = None) -> int | None:
    # Returns either an index of the subseq within the seq, or None.
    # Accepts a function find(seq, subseq), which returns an integer on success
    # and either: None, False, or -1, on failure.
    if find is None:
        try:
            return seq.index(subseq)
        except ValueError:
            return None
    else:
        i = find(seq, subseq)
        return None if (i in (None, -1) or i is False) else i


if os.name == 'posix':

    def _failed(self, status: int = 0):
        if self.status is None or status is None:
            return None
        return _status(self) != status

    def _status(self):
        return self.status
elif os.name == 'nt':

    def _failed(self, status: int = 0):
        return not (self.status is None or status is None) and self.status != status

    def _status(self):
        return self.status


class TestCommon(TestCmd):
    # Additional methods from the Perl Test::Cmd::Common module
    # that we may wish to add in the future:
    #
    #  $test->subdir('subdir', ...);
    #
    #  $test->copy('src_file', 'dst_file');

    def __init__(self, **kw) -> None:
        """Initialize a new TestCommon instance.  This involves just
        calling the base class initialization, and then changing directory
        to the workdir.
        """
        super().__init__(**kw)
        os.chdir(self.workdir)

    def options_arguments(
        self,
        options: str | list[str],
        arguments: str | list[str],
    ):
        """Merges the "options" keyword argument with the arguments."""
        # TODO: this *doesn't* split unless both are non-empty strings.
        #    Did we want to always split strings?
        if options:
            if arguments is None:
                return options

            # If not list, then split into lists
            # this way we're not losing arguments specified with
            # Spaces in quotes.
            if isinstance(options, str):
                options = options.split()
            if isinstance(arguments, str):
                arguments = arguments.split()
            arguments = options + arguments

        return arguments

    def must_be_writable(self, *files) -> None:
        """Ensure that the specified file(s) exist and are writable.

        An individual file can be specified as a list of directory names,
        in which case the pathname will be constructed by concatenating
        them.  Exits FAILED if any of the files does not exist or is
        not writable.
        """
        flist = [os.path.join(*x) if is_List(x) else x for x in files]
        existing, missing = separate_files(flist)
        unwritable = [x for x in existing if not is_writable(x)]
        if missing:
            print("Missing files: `%s'" % "', `".join(missing))
        if unwritable:
            print("Unwritable files: `%s'" % "', `".join(unwritable))
        self.fail_test(missing + unwritable)

    def must_contain(
        self,
        file: str,
        required: str,
        mode: str = 'rb',
        find: Callable | None = None,
    ) -> None:
        """Ensures specified file contains the required text.

        Args:
            file: name of file to search in.
            required (string): text to search for. For the default
              find function, type must match the return type from
              reading the file; current implementation will convert.
            mode: file open mode.
            find: optional custom search routine. Must take the
              form ``find(output, line)``, returning non-negative integer on success
              and None, False, or -1, on failure.

        Calling test exits FAILED if search result is false
        """
        if 'b' in mode:
            # Reading a file in binary mode returns a bytes object.
            # We cannot search for a string in a bytes obj so convert.
            required = to_bytes(required)
        file_contents = self.read(file, mode)

        if not contains(file_contents, required, find):
            print(f"File `{file}' does not contain required string.")
            print(self.banner('Required string '))
            print(required)
            print(self.banner(f'{file} contents '))
            print(file_contents)
            self.fail_test()

    def must_contain_all(
        self, output, input, title: str = "", find: Callable | None = None
    ) -> None:
        """Ensures that the specified output string (first argument)
        contains all of the specified input as a block (second argument).

        An optional third argument can be used to describe the type
        of output being searched, and only shows up in failure output.

        An optional fourth argument can be used to supply a different
        function, of the form "find(output, line)", to use when searching
        for lines in the output.
        """
        if is_List(output):
            output = '\n'.join(output)

        if not contains(output, input, find):
            if not title:
                title = 'output'
            print(f'Missing expected input from {title}:')
            print(input)
            print(self.banner(f"{title} "))
            print(output)
            self.fail_test()

    def must_contain_all_lines(
        self, output, lines, title: str = "", find: Callable | None = None
    ) -> None:
        """Ensures that the specified output string (first argument)
        contains all of the specified lines (second argument).

        An optional third argument can be used to describe the type
        of output being searched, and only shows up in failure output.

        An optional fourth argument can be used to supply a different
        function, of the form "find(output, line)", to use when searching
        for lines in the output.
        """
        if is_List(output):
            output = '\n'.join(output)

        missing = [line for line in lines if not contains(output, line, find)]
        if missing:
            if not title:
                title = 'output'
            sys.stdout.write(f"Missing expected lines from {title}:\n")
            for line in missing:
                sys.stdout.write(f"    {line!r}\n")
            sys.stdout.write(f"{self.banner(f'{title} ')}\n")
            sys.stdout.write(output)
            self.fail_test()

    def must_contain_single_instance_of(self, output, lines, title: str = "") -> None:
        """Ensures that the specified output string (first argument)
        contains one instance of the specified lines (second argument).

        An optional third argument can be used to describe the type
        of output being searched, and only shows up in failure output.
        """
        if is_List(output):
            output = '\n'.join(output)

        counts = {}
        for line in lines:
            count = output.count(line)
            if count != 1:
                counts[line] = count

        if counts:
            if not title:
                title = 'output'
            sys.stdout.write(f"Unexpected number of lines from {title}:\n")
            for line in counts:
                sys.stdout.write(f"    {line!r}: found {str(counts[line])}\n")
            sys.stdout.write(f"{self.banner(f'{title} ')}\n")
            sys.stdout.write(output)
            self.fail_test()

    def must_contain_any_line(
        self, output, lines, title: str = "", find: Callable | None = None
    ) -> None:
        """Ensures that the specified output string (first argument)
        contains at least one of the specified lines (second argument).

        An optional third argument can be used to describe the type
        of output being searched, and only shows up in failure output.

        An optional fourth argument can be used to supply a different
        function, of the form "find(output, line)", to use when searching
        for lines in the output.
        """
        for line in lines:
            if contains(output, line, find):
                return

        if not title:
            title = 'output'
        sys.stdout.write(f"Missing any expected line from {title}:\n")
        for line in lines:
            sys.stdout.write(f"    {line!r}\n")
        sys.stdout.write(f"{self.banner(f'{title} ')}\n")
        sys.stdout.write(output)
        self.fail_test()

    def must_contain_exactly_lines(
        self, output, expect, title: str = "", find: Callable | None = None
    ) -> None:
        """Ensures that the specified output string (first argument)
        contains all of the lines in the expected string (second argument)
        with none left over.

        An optional third argument can be used to describe the type
        of output being searched, and only shows up in failure output.

        An optional fourth argument can be used to supply a different
        function, of the form "find(output, line)", to use when searching
        for lines in the output.  The function must return the index
        of the found line in the output, or None if the line is not found.
        """
        out = output.splitlines()
        if is_List(expect):
            exp = [e.rstrip('\n') for e in expect]
        else:
            exp = expect.splitlines()
        if sorted(out) == sorted(exp):
            # early out for exact match
            return
        missing = []
        for line in exp:
            i = find_index(out, line, find)
            if i is None:
                missing.append(line)
            else:
                out.pop(i)

        if not missing and not out:
            # all lines were matched
            return

        if not title:
            title = 'output'
        if missing:
            sys.stdout.write(f"Missing expected lines from {title}:\n")
            for line in missing:
                sys.stdout.write(f"    {line!r}\n")
            sys.stdout.write(f"{self.banner(f'Missing {title} ')}\n")
        if out:
            sys.stdout.write(f"Extra unexpected lines from {title}:\n")
            for line in out:
                sys.stdout.write(f"    {line!r}\n")
            sys.stdout.write(f"{self.banner(f'Extra {title} ')}\n")
        sys.stdout.flush()
        self.fail_test()

    def must_contain_lines(
        self, lines, output, title: str = "", find: Callable | None = None
    ) -> None:
        # Deprecated; retain for backwards compatibility.
        self.must_contain_all_lines(output, lines, title, find)

    def must_exist(self, *files, message: str = "") -> None:
        """Ensures that the specified file(s) must exist.  An individual
        file be specified as a list of directory names, in which case the
        pathname will be constructed by concatenating them.  Exits FAILED
        if any of the files does not exist.
        """
        flist = [os.path.join(*x) if is_List(x) else x for x in files]
        missing = [x for x in flist if not os.path.exists(x) and not os.path.islink(x)]
        if missing:
            print("Missing files: `%s'" % "', `".join(missing))
            self.fail_test(bool(missing), message=message)

    def must_exist_one_of(self, files, message: str = "") -> None:
        """Ensures that at least one of the specified file(s) exists.
        The filenames can be given as a list, where each entry may be
        a single path string, or a tuple of folder names and the final
        filename that get concatenated.
        Supports wildcard names like 'foo-1.2.3-*.rpm'.
        Exits FAILED if none of the files exists.
        """
        missing = []
        for x in files:
            if is_List(x) or is_Tuple(x):
                xpath = os.path.join(*x)
            else:
                xpath = os.path.join(x) if is_Sequence(x) else x
            if glob.glob(xpath):
                return
            missing.append(xpath)
        print("Missing one of: `%s'" % "', `".join(missing))
        self.fail_test(bool(missing), message=message)

    def must_match(
        self,
        file,
        expect,
        mode: str = 'rb',
        match: Callable | None = None,
        message: str = "",
        newline=None,
    ):
        """Matches the contents of the specified file (first argument)
        against the expected contents (second argument).  The expected
        contents are a list of lines or a string which will be split
        on newlines.
        """
        file_contents = self.read(file, mode, newline)
        if not match:
            match = self.match
        try:
            self.fail_test(
                not match(to_str(file_contents), to_str(expect)),
                message=message,
            )
        except KeyboardInterrupt:
            raise
        except:
            print(f"Unexpected contents of `{file}'")
            self.diff(expect, file_contents, 'contents ')
            raise

    def must_match_file(
        self,
        file,
        golden_file,
        mode: str = 'rb',
        match: Callable | None = None,
        message: str = "",
        newline=None,
    ) -> None:
        """Matches the contents of the specified file (first argument)
        against the expected contents (second argument).  The expected
        contents are a list of lines or a string which will be split
        on newlines.
        """
        file_contents = self.read(file, mode, newline)
        golden_file_contents = self.read(golden_file, mode, newline)

        if not match:
            match = self.match

        try:
            self.fail_test(
                not match(to_str(file_contents), to_str(golden_file_contents)),
                message=message,
            )
        except KeyboardInterrupt:
            raise
        except:
            print(f"Unexpected contents of `{file}'")
            self.diff(golden_file_contents, file_contents, 'contents ')
            raise

    def must_not_contain(self, file, banned, mode: str = 'rb', find=None) -> None:
        """Ensures that the specified file doesn't contain the banned text."""
        file_contents = self.read(file, mode)

        if contains(file_contents, banned, find):
            print(f"File `{file}' contains banned string.")
            print(self.banner('Banned string '))
            print(banned)
            print(self.banner(f'{file} contents '))
            print(file_contents)
            self.fail_test()

    def must_not_contain_any_line(
        self, output, lines, title: str = "", find: Callable | None = None
    ) -> None:
        """Ensures that the specified output string (first argument)
        does not contain any of the specified lines (second argument).

        An optional third argument can be used to describe the type
        of output being searched, and only shows up in failure output.

        An optional fourth argument can be used to supply a different
        function, of the form "find(output, line)", to use when searching
        for lines in the output.
        """
        unexpected = []
        for line in lines:
            if contains(output, line, find):
                unexpected.append(line)

        if unexpected:
            if not title:
                title = 'output'
            sys.stdout.write(f"Unexpected lines in {title}:\n")
            for line in unexpected:
                sys.stdout.write(f"    {line!r}\n")
            sys.stdout.write(f"{self.banner(f'{title} ')}\n")
            sys.stdout.write(output)
            self.fail_test()

    def must_not_contain_lines(
        self, lines, output, title: str = "", find: Callable | None = None
    ) -> None:
        self.must_not_contain_any_line(output, lines, title, find)

    def must_not_exist(self, *files) -> None:
        """Ensures that the specified file(s) must not exist.
        An individual file be specified as a list of directory names, in
        which case the pathname will be constructed by concatenating them.
        Exits FAILED if any of the files exists.
        """
        flist = [os.path.join(*x) if is_List(x) else x for x in files]
        existing = [x for x in flist if os.path.exists(x) or os.path.islink(x)]
        if existing:
            print("Unexpected files exist: `%s'" % "', `".join(existing))
            self.fail_test(bool(existing))

    def must_not_exist_any_of(self, files) -> None:
        """Ensures that none of the specified file(s) exists.
        The filenames can be given as a list, where each entry may be
        a single path string, or a tuple of folder names and the final
        filename that get concatenated.
        Supports wildcard names like 'foo-1.2.3-*.rpm'.
        Exits FAILED if any of the files exists.
        """
        existing = []
        for x in files:
            if is_List(x) or is_Tuple(x):
                xpath = os.path.join(*x)
            else:
                xpath = os.path.join(x) if is_Sequence(x) else x
            if glob.glob(xpath):
                existing.append(xpath)
        if existing:
            print("Unexpected files exist: `%s'" % "', `".join(existing))
            self.fail_test(bool(existing))

    def must_not_be_empty(self, file) -> None:
        """Ensures that the specified file exists, and that it is not empty.
        Exits FAILED if the file doesn't exist or is empty.
        """
        if not (os.path.exists(file) or os.path.islink(file)):
            print(f"File doesn't exist: `{file}'")
            self.fail_test(file)

        try:
            fsize = os.path.getsize(file)
        except OSError:
            fsize = 0

        if fsize == 0:
            print(f"File is empty: `{file}'")
            self.fail_test(file)

    def must_not_be_writable(self, *files) -> None:
        """Ensures that the specified file(s) exist and are not writable.
        An individual file can be specified as a list of directory names,
        in which case the pathname will be constructed by concatenating
        them.  Exits FAILED if any of the files does not exist or is
        writable.
        """
        flist = [os.path.join(*x) if is_List(x) else x for x in files]
        existing, missing = separate_files(flist)
        writable = [file for file in existing if is_writable(file)]
        if missing:
            print("Missing files: `%s'" % "', `".join(missing))
        if writable:
            print("Writable files: `%s'" % "', `".join(writable))
        self.fail_test(missing + writable)

    def _complete(
        self,
        actual_stdout,
        expected_stdout,
        actual_stderr,
        expected_stderr,
        status,
        match,
    ) -> None:
        """
        Post-processes running a subcommand, checking for failure
        status and displaying output appropriately.
        """
        if _failed(self, status):
            expect = ''
            if status != 0:
                expect = f" (expected {str(status)})"
            print(f"{self.program} returned {_status(self)}{expect}")
            print(self.banner('STDOUT '))
            print(actual_stdout)
            print(self.banner('STDERR '))
            print(actual_stderr)
            self.fail_test()
        if expected_stdout is not None and not match(actual_stdout, expected_stdout):
            self.diff(expected_stdout, actual_stdout, 'STDOUT ')
            if actual_stderr:
                print(self.banner('STDERR '))
                print(actual_stderr)
            self.fail_test()
        if expected_stderr is not None and not match(actual_stderr, expected_stderr):
            print(self.banner('STDOUT '))
            print(actual_stdout)
            self.diff(expected_stderr, actual_stderr, 'STDERR ')
            self.fail_test()

    def start(
        self,
        program=None,
        interpreter=None,
        options=None,
        arguments=None,
        universal_newlines=None,
        **kw,
    ):
        """
        Starts a program or script for the test environment, handling
        any exceptions.
        """
        arguments = self.options_arguments(options, arguments)
        try:
            return super().start(
                program, interpreter, arguments, universal_newlines, **kw
            )
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(self.banner('STDOUT '))
            try:
                print(self.stdout())
            except IndexError:
                pass
            print(self.banner('STDERR '))
            try:
                print(self.stderr())
            except IndexError:
                pass
            cmd_args = self.command_args(program, interpreter, arguments)
            sys.stderr.write(f'Exception trying to execute: {cmd_args}\n')
            raise e

    def finish(
        self,
        popen,
        stdout: str | None = None,
        stderr: str | None = '',
        status: int | None = 0,
        **kw,
    ) -> None:
        """Finish and wait for the process being run.

        The *popen* argument describes a ``Popen`` object controlling
        the process.

        The default behavior is to expect a successful exit, to not test
        standard output, and to expect error output to be empty.

        Only arguments extending :meth:`TestCmd.finish` are shown.

        Args:
            stdout:  The expected standard output from the command.
               A value of ``None`` means don't test standard output.
            stderr:  The expected error output from the command.
               A value of ``None`` means don't test error output.
            status:  The expected exit status from the command.
               A value of ``None`` means don't test exit status.
        """
        super().finish(popen, **kw)
        match = kw.get('match', self.match)
        self._complete(self.stdout(), stdout, self.stderr(), stderr, status, match)

    def run(
        self,
        options=None,
        arguments=None,
        stdout: str | None = None,
        stderr: str | None = '',
        status: int | None = 0,
        **kw,
    ) -> None:
        """Runs the program under test, checking that the test succeeded.

        The default behavior is to expect a successful exit, not test
        standard output, and expects error output to be empty.

        Only arguments extending :meth:`TestCmd.run` are shown.

        Args:
            options: Extra options that get prepended to the beginning
               of the arguments.
            stdout:  The expected standard output from the command.
               A value of ``None`` means don't test standard output.
            stderr:  The expected error output from the command.
               A value of ``None`` means don't test error output.
            status:  The expected exit status from the command.
               A value of ``None`` means don't test exit status.

        By default, this expects a successful exit (status = 0), does
        not test standard output (stdout = None), and expects that error
        output is empty (stderr = "").
        """
        kw['arguments'] = self.options_arguments(options, arguments)
        try:
            match = kw.pop('match')
        except KeyError:
            match = self.match
        super().run(**kw)
        self._complete(self.stdout(), stdout, self.stderr(), stderr, status, match)

    def skip_test(
        self, message: str = "Skipping test.\n", from_fw: bool = False
    ) -> None:
        """Skips a test.

        Proper test-skipping behavior is dependent on the external
        TESTCOMMON_PASS_SKIPS environment variable.  If set, we treat
        the skip as a PASS (exit 0), and otherwise treat it as NO RESULT.
        In either case, we print the specified message as an indication
        that the substance of the test was skipped.

        The use case for treating the skip as a PASS was an old system
        that the SCons project has not used for a long time, and that
        code path could eventually be dropped.

        When reporting a NO RESULT, we normally skip the top line of the
        traceback, as from no_result()'s point of view, that is this
        function, and the user is likely to only be interested in the
        test that called us. If from_fw is True, the skip was initiated
        indirectly, coming from some function in the framework
        (test_for_tool, skip_if_msvc, etc.), in this case we want to
        skip an additional line to eliminate that function as well.

        Args:
            message: text to include in the skip message. Callers
                should normally provide a reason, to improve on the default.
            from_fw: if true, skip an extra line of traceback.
        """
        if message:
            sys.stdout.write(message)
            if not message.endswith('\n'):
                sys.stdout.write('\n')
            sys.stdout.flush()
        pass_skips = os.environ.get('TESTCOMMON_PASS_SKIPS')
        if pass_skips in [None, 0, '0']:
            if from_fw:
                self.no_result(skip=2)
            else:
                self.no_result(skip=1)
        else:
            # We're under the development directory for this change,
            # so this is an Aegis invocation; pass the test (exit 0).
            self.pass_test()

    @staticmethod
    def detailed_diff(value, expect) -> str:
        v_split = value.split('\n')
        e_split = expect.split('\n')
        if len(v_split) != len(e_split):
            print(f"different number of lines:{len(v_split)} {len(e_split)}")

        for v, e in zip(v_split, e_split):
            # print(f"{v}:{e}")
            if v != e:
                print(f"\n[{v}]\n[{e}]")

        return f"Expected:\n{expect}\nGot:\n{value}"


# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
