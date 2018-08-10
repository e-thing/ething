# coding: utf-8

from .ResourceEvent import ResourceSignal, ResourceEvent, ResourceFilter, attr


class FileDataModified(ResourceSignal):
    pass


@attr('resource', type=ResourceFilter(onlyTypes=('resources/File',)))
class FileDataModifiedEvent(ResourceEvent):
    """
    is emitted each time file's content is modified
    """
    signal = FileDataModified
