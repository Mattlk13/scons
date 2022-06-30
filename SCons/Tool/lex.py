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
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Tool-specific initialization for lex.

This tool should support multiple lex implementations,
but is in actuality biased towards GNU Flex.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.
"""

import os.path
import sys
from typing import Optional

import SCons.Action
import SCons.Tool
import SCons.Warnings
from SCons.Platform.mingw import MINGW_DEFAULT_PATHS
from SCons.Platform.cygwin import CYGWIN_DEFAULT_PATHS
from SCons.Platform.win32 import CHOCO_DEFAULT_PATH
from SCons.Util import CLVar, to_String

DEFAULT_PATHS = CHOCO_DEFAULT_PATH + MINGW_DEFAULT_PATHS + CYGWIN_DEFAULT_PATHS

LexAction = SCons.Action.Action("$LEXCOM", "$LEXCOMSTR")

if sys.platform == 'win32':
    BINS = ['flex', 'lex', 'win_flex']
else:
    BINS = ["flex", "lex"]


def lexEmitter(target, source, env) -> tuple:
    """Adds extra files generated by lex program to target list."""

    sourceBase, sourceExt = os.path.splitext(to_String(source[0]))
    if sourceExt == ".lm":           # If using Objective-C
        target = [sourceBase + ".m"] # the extension is ".m".

    # With --header-file and ----tables-file, the file to write is defined
    # by the option argument. Extract this and include in the list of targets.
    # NOTE: a filename passed to the command this way is not modified by SCons,
    # and so will be interpreted relative to the project top directory at
    # execution time, while the name added to the target list will be
    # interpreted relative to the SConscript directory - a possible mismatch.
    #
    # These are GNU flex-only options.
    # TODO: recognize --outfile also?
    file_gen_options = ["--header-file=", "--tables-file="]
    lexflags = env.subst_list("$LEXFLAGS", target=target, source=source)
    for option in lexflags[0]:
        for fileGenOption in file_gen_options:
            l = len(fileGenOption)
            if option[:l] == fileGenOption:
                # A file generating option is present, so add the
                # file name to the target list.
                file_name = option[l:].strip()
                target.append(file_name)

    return target, source


def get_lex_path(env, append_paths=False) -> Optional[str]:
    """
    Returns the path to the lex tool, searching several possible names.

    Only called in the Windows case, so the `default_path` argument to
    :func:`find_program_path` can be Windows-specific.

    Args:
        env: current construction environment
        append_paths: if set, add the path to the tool to PATH
    """
    for prog in BINS:
        bin_path = SCons.Tool.find_program_path(
            env,
            prog,
            default_paths=DEFAULT_PATHS,
            add_path=append_paths,
        )
        if bin_path:
            return bin_path

    SCons.Warnings.warn(
        SCons.Warnings.SConsWarning,
        'lex tool requested, but lex or flex binary not found in ENV PATH'
    )


def generate(env) -> None:
    """Add Builders and construction variables for lex to an Environment."""
    c_file, cxx_file = SCons.Tool.createCFileBuilders(env)

    # C
    c_file.add_action(".l", LexAction)
    c_file.add_emitter(".l", lexEmitter)

    c_file.add_action(".lex", LexAction)
    c_file.add_emitter(".lex", lexEmitter)

    # Objective-C
    cxx_file.add_action(".lm", LexAction)
    cxx_file.add_emitter(".lm", lexEmitter)

    # C++
    cxx_file.add_action(".ll", LexAction)
    cxx_file.add_emitter(".ll", lexEmitter)

    env["LEXFLAGS"] = CLVar("")

    if sys.platform == 'win32':
        # ignore the return - we do not need the full path here
        _ = get_lex_path(env, append_paths=True)
        env["LEX"] = env.Detect(BINS)
        if not env.get("LEXUNISTD"):
            env["LEXUNISTD"] = CLVar("")
        env["LEXCOM"] = "$LEX $LEXUNISTD $LEXFLAGS -t $SOURCES > $TARGET"
    else:
        env["LEX"] = env.Detect(BINS)
        env["LEXCOM"] = "$LEX $LEXFLAGS -t $SOURCES > $TARGET"


def exists(env) -> Optional[str]:
    if sys.platform == 'win32':
        return get_lex_path(env)
    else:
        return env.Detect(BINS)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
