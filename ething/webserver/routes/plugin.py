# coding: utf-8
from flask import send_file


def install(core, app, auth, **kwargs):

    @app.route('/api/plugin/<name>/index.js')
    @auth.required()
    def plugin(name):
        p = core.get_plugin(name)
        if p:
            if p.js_index:
                return send_file(p.js_index)
            else:
                raise Exception('no js index')
        else:
            raise Exception('unknown plugin')
