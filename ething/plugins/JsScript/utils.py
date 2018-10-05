
def addslashes(s):
    l = ["\\", '"', "'", "\0", ]
    for i in l:
        if i in s:
            s = s.replace(i, '\\'+i)
    return s


class Output(object):

    def __init__(self, chunked_output):
        self._chunked_output = chunked_output
        # cached
        self._stderr = None
        self._stdout = None
        self._std = None

    def __str__(self):
        return self.std

    @property
    def chunked(self):
        return self._chunked_output

    @property
    def stderr(self):
        if self._stderr is None:
            self._stderr = self._cat('stderr')
        return self._stderr

    @property
    def stdout(self):
        if self._stdout is None:
            self._stdout = self._cat('stdout')
        return self._stdout

    @property
    def std(self):
        if self._std is None:
            self._std = self._cat()
        return self._std

    def _cat(self, type = None):
        strcat = ''
        for item in self._chunked_output:
            if type is not None and item['type'] != type:
                continue
            strcat += item['chunk'].encode('utf8').decode('unicode_escape', "replace")
        return strcat