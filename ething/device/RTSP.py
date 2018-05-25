# coding: utf-8


from ething.Device import Device, method, attr, isString, isObject, isInteger, isNone, READ_ONLY, Validator
from ething.utils import pingable
from ething.interfaces import Camera
import subprocess
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


@pingable('url')
@attr('url', validator=isString(allow_empty=False, regex='^rtsp://'), description="The URL of the device rtsp://... .")
@attr('transport', validator=isString(allow_empty=False, enum=['udp', 'tcp', 'http']), default='tcp', description="Lower transport protocol. Allowed values are the ones defined for the flags for rtsp_transport (see https://libav.org/avconv.html).")
class RTSP(Device, Camera):
    """
    RTSP Device resource representation, usually IP camera
    """

    @method.return_type('image/jpeg')
    def snapshot(self):
        """
        get a snapshot.
        """
        cmd = "avconv -rtsp_transport %s -i %s -frames:v 1 -an -f image2 pipe:1 2>/dev/null" % (
            self.transport, self.url)

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        out, err = p.communicate()

        return out

    @method.arg('duration', type='integer', minimum=0, maximum=3600)
    @method.arg('format', enable=False)
    @method.return_type('video/mp4')
    def stream(self, duration=0, format='mp4'):
        """
        return a video stream (mp4).
        """

        cmd = ["avconv -rtsp_transport %s -i %s -an" %
               (self.transport, self.url)]

        if format == 'flv':
            cmd.append("-c copy -f flv")
        elif format == 'mp4':
            cmd.append("-c copy -f mp4 -movflags frag_keyframe+empty_moov")
        else:
            raise ValueError('invalid format %s' % str(format))

        if duration:
            cmd.append("-t %d" % int(duration))

        cmd.append("pipe:1")

        cmd = ' '.join(cmd)

        def generate():
            proc = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE
            )

            def read():
                return proc.stdout.read(1024)

            try:
                for chunk in iter(read, ''):
                    yield chunk
                proc.communicate()
            except:
                proc.terminate()
                proc.wait()

        return generate()
