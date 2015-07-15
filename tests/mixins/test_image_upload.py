# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase

from pydocx.export import PyDocXHTMLExporter
import responses

from pydocxs3upload import S3ImageUploadMixin
from pydocxs3upload.test.utils import get_fixture, assert_html_equal, mock_request


class PyDocXHTMLExporterS3ImageUpload(
    S3ImageUploadMixin,
    PyDocXHTMLExporter
):
    pass


class PyDocXHTMLExporterS3ImageUploadTestCase(TestCase):
    exporter = PyDocXHTMLExporterS3ImageUpload

    @responses.activate
    def test_export_docx_to_html_with_image_upload_to_s3(self):
        mock_request()

        docx_file_path = get_fixture('png_basic_resize_linked_photo.docx')

        signed_request = get_fixture('upload_signed_request.json', as_binary=True)

        html_file_content = get_fixture(
            'png_basic_s3_upload.html',
            as_binary=True
        )

        kwargs = {
            's3_upload': signed_request,
            'unique_filename': False
        }

        html = self.exporter(docx_file_path, **kwargs).parsed

        assert_html_equal(html, html_file_content)

    @responses.activate
    def test_export_docx_to_html_unique_filename(self):
        mock_request()

        docx_file_path = get_fixture('png_basic_resize_linked_photo.docx')

        signed_request = get_fixture('upload_signed_request.json', as_binary=True)

        kwargs = {
            's3_upload': signed_request,
            'unique_filename': True
        }

        html = self.exporter(docx_file_path, **kwargs).parsed

        # we can't check here for the exact html content as the file name is
        # generated dynamically so, we use regexp

        self.assertRegexpMatches(html,
                                 'http://pydocx.s3.amazonaws.com/uploads/pydocx/\d+-image\d+.png')

    @responses.activate
    def test_export_external_image(self):
        mock_request()

        responses.add(responses.GET, 'https://www.google.com/images/srpr/logo11w.png',
                      body=get_fixture('logo11w.png'), status=200, content_type='image/png')

        docx_file_path = get_fixture('external_image.docx')

        html_file_content = get_fixture(
            'external_image.html',
            as_binary=True
        )

        signed_request = get_fixture('upload_signed_request.json', as_binary=True)

        kwargs = {
            's3_upload': signed_request,
            'unique_filename': False
        }

        html = self.exporter(docx_file_path, **kwargs).parsed

        assert_html_equal(html_file_content, html)
