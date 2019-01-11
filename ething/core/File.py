# coding: utf-8

from future.utils import text_type, bord
from .Resource import Resource
from .date import TzDate, utcnow
from .entity import *
from .Signal import ResourceSignal
import datetime
import os
from .utils.mime import content_to_mime, ext_to_mime
import re
import base64
try:
    from PIL import Image, ImageOps
except ImportError:
    Image = None
    ImageOps = None
from io import BytesIO


class FileDataModified(ResourceSignal):
    """
    is emitted each time file's content is modified
    """
    pass


@throw(FileDataModified)
@attr('expireAfter', type=Nullable(Integer(min=1)), default=None, description="The amount of time (in seconds) after which this resource will be removed.")
@attr('content', default=None, mode=PRIVATE)
@attr('thumb', default=None, mode=PRIVATE)
@attr('size', default=0, mode=READ_ONLY, description="The size of this resource in bytes")
@attr('isText', default=True, mode=READ_ONLY, description="True if this file has text based content.")
@attr('mime', default='text/plain', mode=READ_ONLY, description="The MIME type of the file (automatically detected from the content).")
@attr('contentModifiedDate', type=TzDate(), default=lambda _: utcnow(), mode=READ_ONLY, description="Last time the content of this file was modified (formatted RFC 3339 timestamp).")
class File(Resource):

    def toJson(self, **kwargs):
        o = super(File, self).toJson(**kwargs)
        o['hasThumbnail'] = bool(self.thumb)
        return o

    def remove(self, removeChildren=False):

        # remove the file from GridFS
        if self.content is not None:
            self.ething.db.removeFile(self.content)

        # remove any thumbnail
        if self.thumb is not None:
            self.ething.db.removeFile(self.thumb)

        # remove the resource
        super(File, self).remove(removeChildren)

    def __setattr__(self,    name, value):
        super(File, self).__setattr__(name, value)

        if name == 'name':
            self.updateMeta(File.META_MIME | File.META_TEXT)

    # must be called regularly by the core
    def checkExpiredData(self):
        # remove the file if the data has expired
        if self.isExpired():
            self.remove()

    def isExpired(self):
        expireAfter = self.expireAfter
        if expireAfter is not None:
            expiratedDate = self.modifiedDate + \
                datetime.timedelta(0, expireAfter)
            return expiratedDate < utcnow()
        return False

    def read(self, encoding=None):
        if self.content is not None:
            contents = self.ething.db.retrieveFile(self.content)
        else:
            contents = None

        if contents is None:
            contents = b''

        if encoding is not None:
            contents = contents.decode(encoding)

        return contents

    def write(self, bytes, encoding=None):

        with self:
            if isinstance(bytes, text_type):
                if encoding is None:
                    raise Exception('No encoding specified')
                bytes = bytes.encode(encoding)

            # remove that file if it exists
            if self.content is not None:
                self.ething.db.removeFile(self.content)
            self.content = None
            self.size = 0

            if bytes:
                self.content = self.ething.db.storeFile('File/%s/content' % self.id, bytes, {
                    'parent': self.id
                })
                self.size = self.ething.db.getFileSize(self.content)

            self.contentModifiedDate = utcnow()

            self.updateMeta(File.META_ALL, bytes)

        # generate an event
        self.dispatchSignal(FileDataModified(self))

        return True

    def append(self, bytes, encoding=None):
        if isinstance(bytes, text_type):
            if encoding is None:
                raise Exception('No encoding specified')
            bytes = bytes.encode(encoding)

        d = self.read()
        d += bytes
        return self.write(d)

    # update meta information : mimeType, isText and thumbnail
    META_MIME = 1
    META_TEXT = 2
    META_THUMB = 4
    META_ALL = 255
    META_NONE = 0
    # the content can be provided to avoid reading it from the database

    def updateMeta(self, opt=META_ALL, content=None):

        with self:
            if opt & File.META_MIME:
                # try to find the correct mime type according to the extension first, then if not found, by the content

                mime = None
                filename, ext = os.path.splitext(self.name)
                ext = ext[1:]

                if ext:
                    mime = ext_to_mime(ext)

                if mime is None:
                    # try to get the mime type from the content
                    if content is None:
                        content = self.read()
                    if content:
                        mime = content_to_mime(content)

                if mime is None:
                    mime = 'text/plain' # default

                self.mime = mime

            if opt & File.META_TEXT:

                isText = None
                mime = self.mime
                m = re.search('^text', mime.lower())
                if m is not None:
                    isText = True
                else:
                    m = re.search('^(image|audio|video)', mime.lower())
                    if m is not None:
                        isText = False

                # other mime type are undetermined
                if isText is None:
                    if not content:
                        content = self.read()

                    isText = File.isPrintable(content)

                self.isText = isText

            if opt & File.META_THUMB:

                if not content:
                    content = self.read()

                thumb = None
                mime = self.mime
                m = re.search('^image', mime.lower())
                if content and m is not None:
                    try:
                        thumb = File.createThumb(content, 128)
                    except:
                        pass

                if self.thumb is not None:
                    self.ething.db.removeFile(self.thumb)
                self.thumb = None

                if thumb:
                    self.thumb = self.ething.db.storeFile('App/%s/thumb' % self.id, thumb, {
                        'parent': self.id
                    })


    @staticmethod
    def isPrintable(content, limit=1000):

        l = min(limit, len(content))

        for i in range(0, l):
            code = bord(content[i])

            if (code < 32 or code > 126) and code != 9 and code != 10 and code != 13 and (code < 128 or code > 254):
                return False

        return True

    def readThumbnail(self):
        return self.ething.db.retrieveFile(self.thumb) if self.thumb is not None else None

    @staticmethod
    def createThumb(imagedata, thumbWidth):
        if Image is None:
            return None
        inBuffer = BytesIO(imagedata)
        im = Image.open(inBuffer)
        #im.thumbnail((thumbWidth, thumbWidth), Image.ANTIALIAS)
        thumb = ImageOps.fit(im, (thumbWidth, thumbWidth), Image.ANTIALIAS)
        buffer = BytesIO()
        thumb.save(buffer, 'PNG')
        thumbdata = buffer.getvalue()
        buffer.close()
        inBuffer.close()
        return thumbdata

    def _before_insert(self):
        super(File, self)._before_insert()
        self.updateMeta(File.META_ALL)

    def export_instance(self):
        s = super(File, self).export_instance()
        s['content'] = None
        s['thumb'] = None
        d = base64.b64encode(self.read())
        return {
            'object': s,
            'content': d
        }

    @classmethod
    def import_instance(cls, data, context = None):
        instance = super(File, cls).import_instance(data.get('object'), context)
        instance.write(base64.b64decode(data.get('content')))
        return instance
