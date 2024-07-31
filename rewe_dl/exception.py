# -*- coding: utf-8 -*-

# Copyright 2015-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Exception classes used

Class Hierarchy:

Exception
 +-- StoreException
      +-- ExtractionError
      |    +-- AuthenticationError
      |    +-- AuthorizationError
      |    +-- NotFoundError
      |    +-- HttpError
      +-- FormatError
      |    +-- FilenameFormatError
      |    +-- DirectoryFormatError
      +-- FilterError
      +-- InputFileError
      +-- NoExtractorError
      +-- StopExtraction
      +-- TerminateExtraction
      +-- RestartExtraction
"""

from __future__ import annotations


class StoreException(Exception):
    """Base class for Store exceptions"""

    default = None
    msgfmt = None
    code = 1

    def __init__(self, message=None, fmt=True):
        if not message:
            message = self.default
        elif isinstance(message, Exception):
            message = "{}: {}".format(message.__class__.__name__, message)
        if self.msgfmt and fmt:
            message = self.msgfmt.format(message)
        Exception.__init__(self, message)


class ExtractionError(StoreException):
    """Base class for exceptions during information extraction"""


class HttpError(ExtractionError):
    """HTTP request during data extraction failed"""

    default = "HTTP request failed"
    code = 4

    def __init__(self, message, response=None):
        ExtractionError.__init__(self, message)
        self.response = response
        self.status = response.status_code if response else 0


class NotFoundError(ExtractionError):
    """Requested resource (gallery/image) could not be found"""

    msgfmt = "Requested {} could not be found"
    default = "resource (products)"
    code = 8


class AuthorizationError(ExtractionError):
    """Insufficient privileges to access a resource"""

    default = "Insufficient privileges to access the specified resource"
    code = 16


class FormatError(StoreException):
    """Error while building output paths"""

    code = 32


class FilenameFormatError(FormatError):
    """Error while building output filenames"""

    msgfmt = "Applying filename format string failed ({})"


class InputFileError(StoreException):
    """Error when parsing input file"""

    code = 32

    def __init__(self, message, *args):
        StoreException.__init__(self, message % args if args else message)


class NoExtractorError(StoreException):
    """No extractor can handle the given URL"""

    code = 64


class StopExtraction(StoreException):
    """Stop data extraction"""

    def __init__(self, message=None, *args):
        StoreException.__init__(self)
        self.message = message % args if args else message
        self.code = 1 if message else 0


class TerminateExtraction(StoreException):
    """Terminate data extraction"""

    code = 0


class RestartExtraction(StoreException):
    """Restart data extraction"""

    code = 0
