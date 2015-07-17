================
pydocx-s3-images
================

Overview
========
An mixin for PyDocX that uploads the images to an S3 bucket instead of returning them as Data URIs when converting from .docx to html.

Requirements
============

* Python 2.7
* Works on Linux, Windows, Mac OSX, BSD

Install
=======

The quick way::

    pip install pydocx-s3-images


Usage
=====

First of all, to use this mixin, you need to create you own amazon s3 bucket and give public permission so that uploaded images 
can be accessed from generated html files. `Here <http://docs.aws.amazon.com/AmazonS3/latest/gsg/CreatingABucket.html>`_ you can find a guide
how to do that. Once we have the bucket created, we need to generate a singed request that will be used to upload data to s3.
So, because of this signed request you have full control over the uploaded images. Using `this gist <https://gist.github.com/botzill/059cd690b376011d805a>`_
you can simple generate such signature using boto library.

Here is an example of mixin usage:

.. code-block:: python

    from pydocx.export import PyDocXHTMLExporter
    from pydocxs3upload import S3ImageUploadMixin
    
    class PyDocXHTMLExporterS3ImageUpload(S3ImageUploadMixin, PyDocXHTMLExporter):
        pass
    
    docx_path = 'path/to/file/doc.docx'
    signed_request = '<signed json string>'
    exporter = PyDocXHTMLExporterS3ImageUpload(docx_path, s3_upload=signed_request)
    
    html = exporter.parsed

Note that you can use the same signed request to convert any docs you want. So, in order to avoid uploading images with the same name and
overriding previous one, each image is appended a timestamp which makes it unique. If, for some reasons, you don't want this feature by default
you can change it by passing parameter ``'unique_filename': False``.

.. code-block:: python

    exporter = PyDocXHTMLExporterS3ImageUpload(docx_path, 
        s3_upload=signed_request, unique_filename=False)

In this case all images are named as ``image1, image2, ..., imagen``. 