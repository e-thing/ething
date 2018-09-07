# coding: utf-8


from flask import send_from_directory, redirect, url_for, request


def install(core, app, auth, **kwargs):

    # static files

    @app.route('/favicon.ico')
    def favicon():
        return '', 404

    @app.route('/')
    def root():
        params = dict(request.args)  # keep query parameter in the redirected url
        params['path'] = 'index.html'
        return redirect(url_for('static_client', **params))

    @app.route('/client')
    def root_client():
        params = dict(request.args) # keep query parameter in the redirected url
        params['path'] = 'index.html'
        return redirect(url_for('static_client', **params))

    @app.route('/client/<path:path>')
    def static_client(path):
        return send_from_directory('webserver/webui', path)
