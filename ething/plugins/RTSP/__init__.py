# coding: utf-8
from ething.Device import *
from ething.utils.ping import pingable
from ething.interfaces import Camera
import subprocess
import re
import sys
import logging


LOGGER = logging.getLogger(__name__)


def is_avconv_installed ():
    version = 'unknown'
    try:
        output = subprocess.check_output('avconv -version', shell=True, stderr=subprocess.DEVNULL)
    except:
        return False
    else:
        line0 = output.decode(sys.stdout.encoding or 'utf8').split('\n')[0]
        m = re.search(r'version ([^\s]+)', line0)
        if m:
            version = m.group(1)
    return version


def install(core, options):
    version = is_avconv_installed()
    if not version:
        LOGGER.warning('[RTSP] the program "avconv" is not installed')
        core.notification.warning('the program "avconv" is not installed', title='RTSP', id='rtsp.avconv.check')
    else:
        LOGGER.info('[RTSP] avconv version=%s', version)
        core.notification.remove('rtsp.avconv.check')


@pingable('url')
@attr('url', type=String(allow_empty=False, regex='^rtsp://'), description="The URL of the device rtsp://... .")
@attr('transport', type=String(allow_empty=False, enum=['udp', 'tcp', 'http']), default='tcp',
      description="Lower transport protocol. Allowed values are the ones defined for the flags for rtsp_transport (see https://libav.org/avconv.html).")
class RTSP(Camera):
    """
    RTSP Device resource representation, usually IP camera.
    avconv must be installed (apt-get install libav-tools)
    """

    @method.return_type('image/jpeg')
    def snapshot(self):
        cmd = "avconv -rtsp_transport %s -i %s -frames:v 1 -an -f image2 pipe:1 2>/dev/null" % (
            self.transport, self.url)

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        out, err = p.communicate()

        if p.returncode != 0:
            raise Exception('avconv error. The device may be unavailable.')

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
