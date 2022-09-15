# coding: utf-8

from future.utils import text_type, bord, binary_type
from .Resource import Resource, ResourceType
from .utils.date import TzDate, utcnow
from .reg import *
from .Signal import ResourceSignal
from .flow import ResourceNode
import os
from .utils.mime import content_to_mime, ext_to_mime


class FileDataModified(ResourceSignal):
    """
    is emitted each time file's content is modified
    """
    pass


@throw(FileDataModified)
@attr('content', default=None, mode=PRIVATE)
@attr('size', default=0, mode=READ_ONLY, description="The size of this resource in bytes")
@attr('mime', default='text/plain', mode=READ_ONLY, description="The MIME type of the file (automatically detected from the content or file extension).")
@attr('contentModifiedDate', type=TzDate(), default=lambda _: utcnow(), mode=READ_ONLY, description="Last time the content of this file was modified (formatted RFC 3339 timestamp).")
class File(Resource):
    """
    The File resource is used to store data.

    Example::

        f = core.create('resources/File', {
            'name': 'foo.txt'
        })

        f.write('bar', encoding='utf8')

        f.read(encoding='utf8') # = 'bar'
    """

    def remove(self):

        # remove the file from GridFS
        if self.content is not None:
            self.core.db.fs.remove(self.content)

        # remove the resource
        super(File, self).remove()

    def __watch__(self, attr, value, old_value):
        if attr.name == 'name':
            self._updateMeta(File.META_MIME)
        super(File, self).__watch__(attr, value, old_value)

    def read(self, encoding=None):
        """
        Return the content of this file.

        :param encoding: If encoding is set, the binary content will be decoded. Else (default), a binary string will be returned.
        :return: the content of the file.
        """
        if self.content is not None:
            contents = self.core.db.fs[self.content].read()
        else:
            contents = None

        if contents is None:
            contents = b''

        if encoding:
            contents = contents.decode(encoding)

        return contents

    def write(self, bytes, encoding=None, append=False):
        """
        Write a content into the file.

        :param bytes: The content. Either a binary string or a text string (Thus the encoding parameter is mandatory).
        :param encoding: The encoding of the content. Mandatory if the bytes parameter is not a binary string.
        :param append: If True, the content will be appended.
        """
        with self:
            if isinstance(bytes, text_type):
                if encoding is None:
                    encoding='UTF-8'
                bytes = bytes.encode(encoding, errors='replace')

            if append:
                bytes = self.read() + bytes

            # remove that file if it exists
            if self.content is not None:
                self.core.db.fs.remove(self.content)
            self.content = None
            self.size = 0

            f = self.core.db.fs.create('File/%s/content' % self.id, bytes, parent=self.id)
            self.content = f.id
            self.size = f.size

            self.contentModifiedDate = utcnow()

            self._updateMeta(File.META_ALL, bytes)

        # generate an event
        self.emit(FileDataModified(self))

    # update meta information : mimeType
    META_MIME = 1
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

    def __db_save__(self, insert):
        super(File, self).__db_save__(insert)
        if insert:
            self._updateMeta(File.META_ALL)


@meta(icon='mdi-file', label="File out", category="storage")
@attr('encoding', type=String(), default='utf8')
@attr('append', type=Boolean(), default=False)
@attr('resource', type=ResourceType(accepted_types=('resources/File',)))
class FileWrite(ResourceNode):
    """ Write the payload content to a file """

    INPUTS = ['default']

    def main(self, **inputs):
        msg = inputs.get('default')
        file = self.resource
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
        file = self.resource
        content = file.read(encoding=self.encoding or None)
        self.emit(content)
