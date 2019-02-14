# coding: utf-8

from future.utils import text_type, bord, binary_type
from .Resource import Resource, ResourceType
from .utils.date import TzDate, utcnow
from .reg import *
from .Signal import ResourceSignal
from .flow import ResourceNode
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
@attr('content', default=None, mode=PRIVATE)
@attr('thumb', default=None, mode=PRIVATE)
@attr('size', default=0, mode=READ_ONLY, description="The size of this resource in bytes")
@attr('mime', default='text/plain', mode=READ_ONLY, description="The MIME type of the file (automatically detected from the content or file extension).")
@attr('contentModifiedDate', type=TzDate(), default=lambda _: utcnow(), mode=READ_ONLY, description="Last time the content of this file was modified (formatted RFC 3339 timestamp).")
class File(Resource):

    @attr('hasThumbnail')
    def hasThumbnail(self):
        return bool(self.thumb)

    def remove(self, removeChildren=False):

        # remove the file from GridFS
        if self.content is not None:
            self.ething.db.fs.remove(self.content)

        # remove any thumbnail
        if self.thumb is not None:
            self.ething.db.fs.remove(self.thumb)

        # remove the resource
        super(File, self).remove(removeChildren)

    def __watch__(self, attr, value, old_value):
        if attr.name == 'name':
            self._updateMeta(File.META_MIME)

    def read(self, encoding=None):
        if self.content is not None:
            contents = self.ething.db.fs[self.content].read()
        else:
            contents = None

        if contents is None:
            contents = b''

        if encoding:
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
                self.ething.db.fs.remove(self.content)
            self.content = None
            self.size = 0

            if bytes:
                f = self.ething.db.fs.create('File/%s/content' % self.id, bytes, parent=self.id)
                self.content = f.id
                self.size = f.size

            self.contentModifiedDate = utcnow()

            self._updateMeta(File.META_ALL, bytes)

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

    # update meta information : mimeType and thumbnail
    META_MIME = 1
    META_THUMB = 2
    META_ALL = 255
    META_NONE = 0
    # the content can be provided to avoid reading it from the database

    def _updateMeta(self, opt=META_ALL, content=None):

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
                    self.ething.db.fs.remove(self.thumb)
                self.thumb = None

                if thumb:
                    f = self.ething.db.fs.create('File/%s/thumb' % self.id, thumb, parent=self.id)
                    self.thumb = f.id

    def readThumbnail(self):
        return self.ething.db.fs[self.thumb].read() if self.thumb is not None else None

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

    def __db_save__(self, insert):
        super(File, self).__db_save__(insert)
        if insert:
            self._updateMeta(File.META_ALL)

    def __export__(self, core):
        s = super(File, self).__export__(core)
        s['content'] = None
        s['thumb'] = None
        d = base64.b64encode(self.read())
        return {
            'object': s,
            'content': d
        }

    @classmethod
    def __import__(cls, data, core):
        instance = super(File, cls).__import__(data.get('object'), core)
        instance.write(base64.b64decode(data.get('content')))
        return instance


@meta(icon='mdi-file', label="File out", category="storage")
@attr('encoding', type=String(), default='utf8')
@attr('append', type=Boolean(), default=False)
@attr('resource', type=ResourceType(accepted_types=('resources/File',)))
class FileWrite(ResourceNode):
    """ Write content to a file """

    INPUTS = ['default']

    def main(self, **inputs):
        msg = inputs.get('default')
        file = self.ething.get(self.resource)
        content = msg.payload
        if not (isinstance(content, string_types) or isinstance(content, binary_type)):
            content = str(content)
        if self.append:
            file.append(content, encoding=self.encoding)
        else:
            file.write(content, encoding=self.encoding)


@meta(icon='mdi-file', label="File In", category="storage")
@attr('encoding', type=String(), default='utf8')
@attr('resource', type=ResourceType(accepted_types=('resources/File',)))
class FileRead(ResourceNode):
    """ Read content of a file """

    INPUTS = ['default']
    OUTPUTS = ['default']

    def main(self, **inputs):
        msg = inputs.get('default')
        file = self.ething.get(self.resource)
        content = file.read(encoding=self.encoding or None)
        self.emit(content)
