from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import re
import os.path
from xml.dom import minidom
import cgi
import json
import base64

import responses

from six.moves.urllib.parse import urlparse, urljoin

from io import BytesIO


def prettify(xml_string):
    """Return a pretty-printed XML string for the Element.
    """
    parsed = minidom.parseString(xml_string)
    return parsed.toprettyxml(indent='\t')


def html_is_equal(a, b):
    a = collapse_html(a)
    b = collapse_html(b)
    return a == b


def assert_html_equal(actual_html, expected_html, filename=None):
    if not html_is_equal(actual_html, expected_html):
        html = prettify(actual_html)
        if filename:
            with open('tests/failures/%s.html' % filename, 'w') as f:
                f.write(html)
        raise AssertionError(html)


def collapse_html(html):
    """
    Remove insignificant whitespace from the html.

    >>> print(collapse_html('''\\
    ...     <h1>
    ...         Heading
    ...     </h1>
    ... '''))
    <h1>Heading</h1>
    >>> print(collapse_html('''\\
    ...     <p>
    ...         Paragraph with
    ...         multiple lines.
    ...     </p>
    ... '''))
    <p>Paragraph with multiple lines.</p>
    """

    def smart_space(match):
        # Put a space in between lines, unless exactly one side of the line
        # break butts up against a tag.
        before = match.group(1)
        after = match.group(2)
        space = ' '
        if before == '>' or after == '<':
            space = ''
        return before + space + after

    # Replace newlines and their surrounding whitespace with a single space (or
    # empty string)
    html = re.sub(
        r'(>?)\s*\n\s*(<?)',
        smart_space,
        html,
    )
    return html.strip()


def get_fixture(fix_name, as_binary=False):
    """Get fixture as path or binary data"""

    file_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        '..',
        'tests',
        'fixtures',
        fix_name,
    )

    if as_binary:
        mode = 'r'
        _, ext = os.path.splitext(fix_name)
        if ext not in ['.html', '.json', '.xml']:
            mode = 'rb'

        with open(file_path, mode) as f:
            return f.read()
    else:
        return file_path


def _get_bucket_name(policy):
    policy_data = json.loads(base64.b64decode(policy))

    bucket_name = None

    for item in policy_data['conditions']:
        if isinstance(item, dict) and item.get('bucket', None):
            bucket_name = item['bucket']
            break

    return bucket_name


def mock_request(url=None, method=responses.POST, status=204, body='',
                 fixture=None, content_type='', include_location=True):
    """Helper to mock requests to amazon s3"""

    if fixture:
        body = get_fixture(fixture, as_binary=True)
        if fixture.endswith('.xml'):
            content_type = 'application/xml'

    def request_callback(request):
        """Get the request that we make and compose the image url"""

        if include_location:
            o = urlparse(request.url)

            rbody = request.body

            _, pdict = cgi.parse_header(request.headers['Content-Type'])
            pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')
            data = cgi.parse_multipart(BytesIO(rbody), pdict)

            # TODO find a better way to take filename
            filename = re.search(r'filename="(.+?)"', str(rbody)).group(1)

            key_name_string = data['key'][0].decode("utf-8")
            policy = data['policy'][0].decode("utf-8")

            key_name = key_name_string.replace('${filename}', filename)
            bucket_name = _get_bucket_name(policy)

            img_url = urljoin('http://%s.s3.amazonaws.com/' % bucket_name,
                              key_name)
            img_url = img_url.replace('http', o.scheme)

            # Make sure we return the image url the same as AWS.
            # Add other headers here
            headers = {'location': img_url}
        else:
            headers = {}

        return status, headers, body

    url = url or 'http://pydocx.s3.amazonaws.com/'

    responses.add_callback(method, url, content_type=content_type,
                           callback=request_callback)
