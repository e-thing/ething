# coding: utf-8

from .ResourceEvent import ResourceSignal, ResourceEvent, isResourceFilter, attr, isNone


class FileDataModified(ResourceSignal):
    pass


@attr('resource', validator = isResourceFilter(onlyTypes = ('File',)) | isNone())
class FileDataModifiedEvent(ResourceEvent):
    """
    is emitted each time file's content is modified
    """
    signal = FileDataModified
    