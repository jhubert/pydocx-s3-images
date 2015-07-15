from __future__ import (
    unicode_literals,
)

import re

try:
    # Python 3
    from urllib.parse import unquote
except ImportError:
    # Python 2
    from urlparse import unquote

IMAGE_DATA_URI_REGEX = re.compile(
    r'data:image/(?P<extension>\w+);base64,(?P<image_data>.+)',
)


def is_encoded_image_uri(image_data):
    """Check if input is a image data format"""

    return IMAGE_DATA_URI_REGEX.match(image_data)


def sanitize_filename(filename):
    """
    When we create attachments from pydocx we usually add a timestamp followed
    by a dash (-) to make the image unique for round-tripping. In an effort to
    prevent a bunch of timestamps preceding the image name (in the event a
    document is round-tripped several times), strip off the timestamp
    and dash. When images come from docx they are always `image\d+`. We only
    want to strip off the timestamp and dash if they were programmatically
    added.
    >>> sanitize_filename('1409764011-image1.gif')
    'image1.gif'
    >>> sanitize_filename('409764011-image1.gif')
    '409764011-image1.gif'
    >>> sanitize_filename('1409764011-image.gif')
    '1409764011-image.gif'
    >>> sanitize_filename('image%20%232014.gif')
    'image #2014.gif'
    """

    # (timestamp)-image(image_number).(file_extension)
    regex = re.compile(r'\d{10}-image\d+\.\w{3,4}')
    if regex.match(filename):
        _, filename = filename.rsplit('-', 1)

    return unquote(filename).encode('utf-8')
