# coding: utf-8
from __future__ import (
    absolute_import,
    unicode_literals,
)

import time

from ..util.image import get_image_data_and_filename
from ..image_upload import S3ImageUploader


class S3ImageUploadMixin(object):
    def __init__(self, *args, **kwargs):
        s3_upload = kwargs.pop('s3_upload', None)
        self.unique_filename = kwargs.pop('unique_filename', True)

        # we may specify a custom uploader class to be used
        uploader_cls = kwargs.pop('uploader_cls', S3ImageUploader)

        super(S3ImageUploadMixin, self).__init__(*args, **kwargs)

        self.image_uploader = uploader_cls(s3_upload)

    def image(self, image_data, filename, x, y, uri_is_external):
        if uri_is_external:
            image_data, filename = get_image_data_and_filename(
                image_data,
                filename,
            )

        if self.unique_filename:
            # make sure that the filename is unique so that it will not rewrite
            # existing images from s3
            filename = "%s-%s" % (str(time.time()).replace('.', ''), filename)

        s3_url = self.image_uploader.upload(image_data, filename)

        image_data = s3_url
        uri_is_external = True

        return super(S3ImageUploadMixin, self).image(
            image_data,
            filename,
            x,
            y,
            uri_is_external
        )
