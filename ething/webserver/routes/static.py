

from flask import send_from_directory, redirect, url_for
import os


def install(core, app, auth, **kwargs):

    # static files

    @app.route('/favicon.ico')
    def favicon():
        return ('', 404)
        #return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

    @app.route('/')
    def root():
        return redirect(url_for('static_client', path = 'index.html'))

    @app.route('/client')
    def root_client():
        return redirect(url_for('static_client', path = 'index.html'))

    @app.route('/client/<path:path>')
    def static_client(path):
        return send_from_directory('webui', path)


        
        