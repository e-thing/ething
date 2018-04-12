# coding: utf-8

from .ResourceEvent import ResourceSignal, ResourceEvent, isResourceFilter, attr, isNone


class FileDataModified(ResourceSignal):
    pass


@attr('resource', validator = isResourceFilter(onlyTypes = ('File',)) | isNone())
class FileDataModifiedEvent(ResourceEvent):
    signal = FileDataModified
    