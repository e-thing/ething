# coding: utf-8

def install(core, app, auth, **kwargs):

    @app.route('/api/start_pairing', methods=['POST'])
    @auth.required()
    def start_pairing():

        core.start_pairing()

        return app.jsonify({
            'pairing': core.is_pairing
        })

    @app.route('/api/stop_pairing', methods=['POST'])
    @auth.required()
    def stop_pairing():

        core.stop_pairing()

        return app.jsonify({
            'pairing': core.is_pairing
        })
