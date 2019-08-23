# coding: utf-8
from flask import send_file


def install(core, app, auth, **kwargs):

    @app.route('/api/plugin/<name>/index.js')
    @auth.required()
    def plugin_js_index(name):
        p = core.plugins[name]
        if p:
            if p.is_js_index_valid():
                return send_file(p.js_index())
            else:
                raise Exception('no js index defined for this plugin')
        else:
            raise Exception('unknown plugin')

    @app.route('/api/plugin')
    @auth.required()
    def plugins():
        return app.jsonify(core.plugins)

    @app.route('/api/plugin/<name>')
    @auth.required()
    def plugin(name):
        p = core.plugins[name]
        if p:
            return app.jsonify(p)
        else:
            raise Exception('unknown plugin')
