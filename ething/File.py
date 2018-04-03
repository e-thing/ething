

from Resource import Resource
import base64
import datetime
import os
import magic
import re
try:
    from PIL import Image, ImageOps
except ImportError:
    Image = None
import cStringIO
from Helpers import dict_recursive_update
from rule.event import FileDataModified
from base import attr, isBool, isString, isNone, isInteger, READ_ONLY, PRIVATE


@attr('expireAfter', validator = isNone() | isInteger(min=1), default = None, description="The amount of time (in seconds) after which this resource will be removed.")
@attr('content', default = None, mode = PRIVATE)
@attr('thumb', default = None, mode = PRIVATE)
@attr('size', default = 0, mode = READ_ONLY, description="The size of this resource in bytes")
@attr('isText', default = True, mode = READ_ONLY, description="True if this file has text based content.")
@attr('mime', default = 'text/plain', mode = READ_ONLY, description="The MIME type of the file (automatically detected from the content).")
@attr('contentModifiedDate', default = datetime.datetime.utcnow(), mode = READ_ONLY, description="Last time the conten of this resource was modified (formatted RFC 3339 timestamp).")
class File(Resource):
    
    def toJson (self):
        o = super(File, self).toJson()
        o['hasThumbnail'] = bool(self._thumb)
        return o
    
    
    
    def remove (self, removeChildren = False):
        
        # remove the file from GridFS
        self.ething.fs.removeFile(self._content)
        
        # remove any thumbnail
        self.ething.fs.removeFile(self._thumb)
        
        # remove the resource
        super(File, self).remove(removeChildren)
    
    
    def __setattr__ (self,    name, value ):
        super(File, self).__setattr__(name, value)
        
        if name == 'name':
            self.updateMeta(File.META_MIME|File.META_TEXT)
    
    
    # must be called regularly by the core
    def checkExpiredData (self):
        # remove the file if the data has expired
        if self.isExpired() :
            self.remove()
    
    def isExpired (self):
        expireAfter = self.expireAfter
        if expireAfter is not None:
            expiratedDate = self.modifiedDate + datetime.timedelta(0,expireAfter)
            return expiratedDate < datetime.datetime.utcnow()
        return False
    
    
    def read (self):
        contents = self.ething.fs.retrieveFile(self._content)
        return contents if contents else ''
    
    
    def write (self, bytes):
        
        # remove that file if it exists
        self.ething.fs.removeFile(self._content)
        self._content = None
        self._size = 0
        
        if bytes:
            self._content = self.ething.fs.storeFile('File/%s/content' % self.id, bytes, {
                'parent' : self.id
            })
            self._size = self.ething.fs.getFileSize(self._content)
        
        
        self._contentModifiedDate = datetime.datetime.utcnow()
        
        self.updateMeta(File.META_ALL, bytes)
        
        self.save()
        
        # generate an event
        self.dispatchSignal(FileDataModified.emit(self))
        
        return True
    
    
    def append (self, bytes):
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
    def updateMeta (self, opt = META_ALL, content = None):
        
        
        if(opt & File.META_MIME):
            """ try to find the correct mime type according to the extension first, then if not found, by the content """
            
            mime = None
            filename, ext = os.path.splitext(self.name)
            ext = ext[1:]
            
            if ext and ext in File.extToMime:
                mime = File.extToMime[ext]
            
            if mime is None:
                # try to get the mime type from the content
                if not content:
                    content = self.read()
                mime = magic.from_buffer(content, mime=True)
            
            
            self._mime = mime
            
        
        
        if(opt & File.META_TEXT):
            
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
            
            
            self._isText = isText
            
        
        
        if(opt & File.META_THUMB):
            
            if not content:
                content = self.read()
            
            thumb = None
            m = re.search('^image', mime.lower())
            if content and m is not None:
                try:
                    thumb = File.createThumb(content,128)
                except:
                    pass
                
            self.ething.fs.removeFile(self._thumb)
            self._thumb = None
            
            if thumb:
                self._thumb = self.ething.fs.storeFile('App/%s/thumb' % self.id, thumb, {
                    'parent' : self.id
                })
            
        
        
        self.save()
        
    
    
    
    
    extToMime = {
      "hqx" : "application/mac-binhex40", 
      "cpt" : "application/mac-compactpro", 
      "doc" : "application/msword", 
      "bin" : "application/octet-stream", 
      "dms" : "application/octet-stream", 
      "lha" : "application/octet-stream", 
      "lzh" : "application/octet-stream", 
      "exe" : "application/octet-stream", 
      "class" : "application/octet-stream", 
      "so" : "application/octet-stream", 
      "dll" : "application/octet-stream", 
      "oda" : "application/oda", 
      "pdf" : "application/pdf", 
      "ai" : "application/postscript", 
      "eps" : "application/postscript", 
      "ps" : "application/postscript", 
      "smi" : "application/smil", 
      "smil" : "application/smil", 
      "wbxml" : "application/vnd.wap.wbxml", 
      "wmlc" : "application/vnd.wap.wmlc", 
      "wmlsc" : "application/vnd.wap.wmlscriptc", 
      "bcpio" : "application/x-bcpio", 
      "vcd" : "application/x-cdlink", 
      "pgn" : "application/x-chess-pgn", 
      "cpio" : "application/x-cpio", 
      "csh" : "application/x-csh", 
      "dcr" : "application/x-director", 
      "dir" : "application/x-director", 
      "dxr" : "application/x-director", 
      "dvi" : "application/x-dvi", 
      "spl" : "application/x-futuresplash", 
      "gtar" : "application/x-gtar", 
      "hdf" : "application/x-hdf", 
      "js" : "application/javascript",
      "json" : "application/json", 
      "skp" : "application/x-koan", 
      "skd" : "application/x-koan", 
      "skt" : "application/x-koan", 
      "skm" : "application/x-koan", 
      "latex" : "application/x-latex", 
      "nc" : "application/x-netcdf", 
      "cdf" : "application/x-netcdf", 
      "sh" : "application/x-sh", 
      "shar" : "application/x-shar", 
      "swf" : "application/x-shockwave-flash", 
      "sit" : "application/x-stuffit", 
      "sv4cpio" : "application/x-sv4cpio", 
      "sv4crc" : "application/x-sv4crc", 
      "tar" : "application/x-tar", 
      "tcl" : "application/x-tcl", 
      "tex" : "application/x-tex", 
      "texinfo" : "application/x-texinfo", 
      "texi" : "application/x-texinfo", 
      "t" : "application/x-troff", 
      "tr" : "application/x-troff", 
      "roff" : "application/x-troff", 
      "man" : "application/x-troff-man", 
      "me" : "application/x-troff-me", 
      "ms" : "application/x-troff-ms", 
      "ustar" : "application/x-ustar", 
      "src" : "application/x-wais-source", 
      "xhtml" : "application/xhtml+xml", 
      "xht" : "application/xhtml+xml", 
      "zip" : "application/zip", 
      "au" : "audio/basic", 
      "snd" : "audio/basic", 
      "mid" : "audio/midi", 
      "midi" : "audio/midi", 
      "kar" : "audio/midi", 
      "mpga" : "audio/mpeg", 
      "mp2" : "audio/mpeg", 
      "mp3" : "audio/mpeg", 
      "aif" : "audio/x-aiff", 
      "aiff" : "audio/x-aiff", 
      "aifc" : "audio/x-aiff", 
      "m3u" : "audio/x-mpegurl", 
      "ram" : "audio/x-pn-realaudio", 
      "rm" : "audio/x-pn-realaudio", 
      "rpm" : "audio/x-pn-realaudio-plugin", 
      "ra" : "audio/x-realaudio", 
      "wav" : "audio/x-wav", 
      "pdb" : "chemical/x-pdb", 
      "xyz" : "chemical/x-xyz", 
      "bmp" : "image/bmp", 
      "gif" : "image/gif", 
      "ief" : "image/ief", 
      "jpeg" : "image/jpeg", 
      "jpg" : "image/jpeg", 
      "jpe" : "image/jpeg", 
      "png" : "image/png", 
      "tiff" : "image/tiff", 
      "tif" : "image/tif", 
      "djvu" : "image/vnd.djvu", 
      "djv" : "image/vnd.djvu", 
      "wbmp" : "image/vnd.wap.wbmp", 
      "ras" : "image/x-cmu-raster", 
      "pnm" : "image/x-portable-anymap", 
      "pbm" : "image/x-portable-bitmap", 
      "pgm" : "image/x-portable-graymap", 
      "ppm" : "image/x-portable-pixmap", 
      "rgb" : "image/x-rgb", 
      "xbm" : "image/x-xbitmap", 
      "xpm" : "image/x-xpixmap", 
      "xwd" : "image/x-windowdump", 
      "igs" : "model/iges", 
      "iges" : "model/iges", 
      "msh" : "model/mesh", 
      "mesh" : "model/mesh", 
      "silo" : "model/mesh", 
      "wrl" : "model/vrml", 
      "vrml" : "model/vrml", 
      "css" : "text/css", 
      "html" : "text/html", 
      "htm" : "text/html", 
      "asc" : "text/plain", 
      "txt" : "text/plain", 
      "rtx" : "text/richtext", 
      "rtf" : "text/rtf", 
      "sgml" : "text/sgml", 
      "sgm" : "text/sgml", 
      "tsv" : "text/tab-seperated-values", 
      "wml" : "text/vnd.wap.wml", 
      "wmls" : "text/vnd.wap.wmlscript", 
      "etx" : "text/x-setext", 
      "xml" : "text/xml", 
      "xsl" : "text/xml", 
      "mpeg" : "video/mpeg", 
      "mpg" : "video/mpeg", 
      "mpe" : "video/mpeg", 
      "qt" : "video/quicktime", 
      "mov" : "video/quicktime", 
      "mxu" : "video/vnd.mpegurl", 
      "avi" : "video/x-msvideo", 
      "movie" : "video/x-sgi-movie"
    }
    
    @staticmethod
    def isPrintable (content, limit = 1000):
        
        l = min(limit,len(content))
        
        for i in range(0,l):
            code = ord(content[i])
            
            if((code<32 or code>126) and code!=9 and code!=10 and code!=13 and (code<128 or code>254)):
                return False
        
        return True
    
    
    
    
    def readThumbnail (self):
        return self.ething.fs.retrieveFile(self._thumb)
    
    
    @staticmethod
    def createThumb (imagedata, thumbWidth ):
        if Image is None:
            return None
        inBuffer = cStringIO.StringIO(imagedata)
        im = Image.open(inBuffer)
        #im.thumbnail((thumbWidth, thumbWidth), Image.ANTIALIAS)
        thumb = ImageOps.fit(im, (thumbWidth, thumbWidth), Image.ANTIALIAS)
        buffer = cStringIO.StringIO()
        thumb.save(buffer,'PNG')
        thumbdata = buffer.getvalue()
        buffer.close()
        inBuffer.close()
        return thumbdata
    
    
if __name__ == '__main__':
    
    import ething.core
    
    ething = ething.core.Core({
        'db':{
            'database': 'test'
        },
        'log':{
            'level': 'debug'
        }
    })
    
    def testTextFile():
        f = ething.create('File', {
            'name' : 'file1.txt'
        })
        
        f.write('hello world')
        
        print f.toJson()
        
        print f.mime
        
        print f.read()
    
    def testImageFile():
        import requests
        
        r = requests.get('https://www.w3schools.com/w3css/img_fjords.jpg', stream=True)
        if r.status_code == 200:
            r.raw.decode_content = True
            
            print 'create...'
            
            f = ething.create('File', {
                'name' : 'image.jpg'
            })
            
            print 'write...'
            
            f.write(r.content)
            
            print f.mime, f.size
            
            print 'end...'
            textfile = open('/tmp/thumb.png', 'w')
            textfile.write(f.readThumbnail())
            textfile.close()
            textfile = open('/tmp/image.png', 'w')
            textfile.write(f.read())
            textfile.close()
            
            
        
        return
    
    testTextFile()