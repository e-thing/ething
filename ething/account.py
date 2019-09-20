# coding: utf-8
from .Resource import Resource
from .reg import *


@abstract
@meta(icon="mdi-account", description='', loginUrl='')
@attr('logged', type=Boolean(), default=False, mode=READ_ONLY)
class Account(Resource):

    @classmethod
    def __schema__(cls, schema, context=None):
        loginUrl = get_meta(cls, 'loginUrl')
        if loginUrl:
            schema['loginUrl'] = loginUrl
        return schema

