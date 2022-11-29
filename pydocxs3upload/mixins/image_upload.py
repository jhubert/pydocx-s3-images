# coding: utf-8
from __future__ import (
    absolute_import,
    unicode_literals,
)

import time

from ..util.image import get_image_data_and_filename
from ..util.uri import get_uri_filename, uri_is_external
from ..image_upload import S3ImageUploader


class S3ImageUploadMixin(object):
    def __init__(self, *args, **kwargs):
        s3_upload = kwargs.pop('s3_upload', None)
        self.unique_filename = kwargs.pop('unique_filename', True)

        # we may specify a custom uploader class to be used
        uploader_cls = kwargs.pop('uploader_cls', S3ImageUploader)

        super(S3ImageUploadMixin, self).__init__(*args, **kwargs)

        self.image_uploader = uploader_cls(s3_upload)

    def get_image_tag(self, image, width=None, height=None, **kwargs):
        if self.first_pass or not image:
            return ''

        filename = get_uri_filename(image.uri)

        if uri_is_external(image.uri):
            image_data, filename = get_image_data_and_filename(
                image.uri,
                filename,
            )
        else:
            image.stream.seek(0)
            image_data = image.stream.read()

        if self.unique_filename:
            # make sure that the filename is unique so that it will not rewrite
            # existing images from s3
            filename = "%s-%s" % (str(time.time()).replace('.', ''), filename)

        s3_url = self.image_uploader.upload(image_data, filename)

        # set the external uri to the amazon s3
        image.uri = s3_url

        return super(S3ImageUploadMixin, self, ).get_image_tag(image,
                                                               width,
                                                               height,
                                                               **kwargs)
