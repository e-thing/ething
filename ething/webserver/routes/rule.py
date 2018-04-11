# coding: utf-8


from flask import request, Response
from ..server_utils import *

def install(core, app, auth, **kwargs):

    @app.route('/api/rules', methods=['GET', 'POST'])
    @auth.required(GET = 'rule:read', POST = 'rule:write')
    def rules():
        
        if request.method == 'GET':
            return jsonify(core.findRules())
        
        elif request.method == 'POST':
            
            data = request.get_json()
            
            if isinstance(data, dict):
                rule = core.createRule(data)
                if rule:
                    response = jsonify(rule)
                    response.status_code = 201
                    return response
                else:
                    raise Exception('Unable to create the rule');
            
            raise Exception('Invalid request');

    
    @app.route('/api/rules/<id>', methods=['GET', 'DELETE', 'PATCH'])
    @auth.required(GET = 'rule:read', DELETE = 'rule:admin', PATCH = 'rule:admin')
    def rule(id):
        
        rules = core.findRules({
            '_id' : id
        });
        
        if len(rules) == 0:
            raise Exception('Unknown rule with id = %s' % id);
        
        rule = rules[0]
        
        if request.method == 'GET':
            return jsonify(rule)
        
        elif request.method == 'DELETE':
            rule.remove()
            return ('', 204)
        
        elif request.method == 'PATCH':
            
            data = request.get_json()
            
            if isinstance(data, dict) and rule.set(data):
                return jsonify(rule)
            
            raise Exception('Invalid request');
