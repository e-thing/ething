# coding: utf-8
from flask import send_file


def install(core, app, auth, **kwargs):

    def plugin_to_json(p):
        return {
            'loaded': p.loaded,
            'config': p.config
        }

    @app.route('/api/plugin/<name>/index.js')
    @auth.required()
    def plugin_js_index(name):
        p = core.get_plugin(name)
        if p:
            if p.JS_INDEX:
                return send_file(p.JS_INDEX)
            else:
                raise Exception('no js index defined for this plugin')
        else:
            raise Exception('unknown plugin')


    @app.route('/api/plugin')
    @auth.required()
    def plugins():

        status = {}
        for p in core.plugins:
            status[p.name] = plugin_to_json(p)

        return app.jsonify(status)

    @app.route('/api/plugin/<name>')
    @auth.required()
    def plugin(name):

        p = core.get_plugin(name)
        if p:
            return app.jsonify(plugin_to_json(p))
        else:
            raise Exception('unknown plugin')

    @app.route('/api/plugin/<name>/load', methods=['POST'])
    @auth.required()
    def plugin_load(name):
        p = core.get_plugin(name)
        if p:
            p.load()
            return app.jsonify(plugin_to_json(p))
        else:
            raise Exception('unknown plugin')

    @app.route('/api/plugin/<name>/unload', methods=['POST'])
    @auth.required()
    def plugin_unload(name):
        p = core.get_plugin(name)
        if p:
            p.unload()
            return app.jsonify(plugin_to_json(p))
        else:
            raise Exception('unknown plugin')
