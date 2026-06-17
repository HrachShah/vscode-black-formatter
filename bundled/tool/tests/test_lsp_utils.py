# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Unit tests for lsp_utils.is_stdlib_file prefix boundary handling."""

from __future__ import annotations

import sys
import pathlib

import pytest

# Ensure bundled/tool is on sys.path so we can import lsp_utils directly.
_TOOL_DIR = str(pathlib.Path(__file__).parent.parent)
if _TOOL_DIR not in sys.path:
    sys.path.insert(0, _TOOL_DIR)

import lsp_utils  # noqa: E402


class TestIsStdlibFile:
    """Verify is_stdlib_file does not match sibling directories that
    share a prefix with a stdlib path."""

    def test_exact_match(self, tmp_path):
        # An exact stdlib directory match returns True.
        stdlib_dir = tmp_path / "lib" / "python3.12"
        stdlib_dir.mkdir(parents=True)
        target = stdlib_dir / "foo.py"
        target.write_text("")
        # Patch the module's stdlib paths to use our tmp dir.
        original = lsp_utils._stdlib_paths.copy()
        lsp_utils._stdlib_paths = {str(stdlib_dir)}
        try:
            assert lsp_utils.is_stdlib_file(str(target)) is True
        finally:
            lsp_utils._stdlib_paths = original

    def test_nested_match(self, tmp_path):
        # A nested file inside the stdlib root returns True.
        stdlib_dir = tmp_path / "lib" / "python3.12"
        nested = stdlib_dir / "site-packages" / "mypkg"
        nested.mkdir(parents=True)
        target = nested / "foo.py"
        target.write_text("")
        original = lsp_utils._stdlib_paths.copy()
        lsp_utils._stdlib_paths = {str(stdlib_dir)}
        try:
            assert lsp_utils.is_stdlib_file(str(target)) is True
        finally:
            lsp_utils._stdlib_paths = original

    def test_sibling_with_shared_prefix_does_not_match(self, tmp_path):
        # Regression: a sibling directory that shares a common prefix
        # with a stdlib path (e.g. python3.12_backup vs python3.12)
        # must NOT be considered part of the stdlib.
        stdlib_dir = tmp_path / "lib" / "python3.12"
        stdlib_dir.mkdir(parents=True)
        sibling = tmp_path / "lib" / "python3.12_backup"
        sibling.mkdir(parents=True)
        target = sibling / "foo.py"
        target.write_text("")
        original = lsp_utils._stdlib_paths.copy()
        lsp_utils._stdlib_paths = {str(stdlib_dir)}
        try:
            assert lsp_utils.is_stdlib_file(str(target)) is False
        finally:
            lsp_utils._stdlib_paths = original

    def test_unrelated_path_does_not_match(self, tmp_path):
        stdlib_dir = tmp_path / "lib" / "python3.12"
        stdlib_dir.mkdir(parents=True)
        target = tmp_path / "elsewhere" / "foo.py"
        target.mkdir(parents=True)
        target = target / "foo.py"
        target.write_text("")
        original = lsp_utils._stdlib_paths.copy()
        lsp_utils._stdlib_paths = {str(stdlib_dir)}
        try:
            assert lsp_utils.is_stdlib_file(str(target)) is False
        finally:
            lsp_utils._stdlib_paths = original

    def test_sibling_share_prefix_string(self):
        # A path that is a strict prefix-string-extension of a stdlib
        # path returns False (was True before the fix, because the
        # old code used ``normalized_path.startswith(path)``).
        stdlib_root = "/usr/local/lib/python3.12"
        sibling = "/usr/local/lib/python3.12_backup/foo.py"
        original = lsp_utils._stdlib_paths.copy()
        lsp_utils._stdlib_paths = {stdlib_root}
        try:
            assert lsp_utils.is_stdlib_file(sibling) is False
        finally:
            lsp_utils._stdlib_paths = original
