# coding: utf-8


from flask import request, Response
from ..server_utils import *

def install(core, app, auth, **kwargs):
    
    rules_args = {
        'fields': fields.DelimitedList(fields.Str()),
    }

    @app.route('/api/rules', methods=['GET', 'POST'])
    @use_args(rules_args)
    @auth.required(GET = 'rule:read', POST = 'rule:write')
    def rules(args):
        
        if request.method == 'GET':
            return jsonEncodeFilterByFields(core.findRules(), args['fields'])
        
        elif request.method == 'POST':
            
            data = request.get_json()
            
            if isinstance(data, dict):
                rule = core.createRule(data)
                if rule:
                    response = jsonEncodeFilterByFields(rule, args['fields'])
                    response.status_code = 201
                    return response
                else:
                    raise Exception('Unable to create the rule');
            
            raise Exception('Invalid request');

    rule_get_args = {
        'fields': fields.DelimitedList(fields.Str()),
    }
    rule_patch_args = rule_get_args

    @app.route('/api/rules/<id>', methods=['GET', 'DELETE', 'PATCH'])
    @use_multi_args(GET = rule_get_args, PATCH = (rule_patch_args, ('query',)))
    @auth.required(GET = 'rule:read', DELETE = 'rule:admin', PATCH = 'rule:admin')
    def rule(args, id):
        
        rules = core.findRules({
            '_id' : id
        });
        
        if len(rules) == 0:
            raise Exception('Unknown rule with id = %s' % id);
        
        rule = rules[0]
        
        if request.method == 'GET':
            return jsonEncodeFilterByFields(rule, args['fields'])
        
        elif request.method == 'DELETE':
            rule.remove()
            return ('', 204)
        
        elif request.method == 'PATCH':
            
            data = request.get_json()
            
            if isinstance(data, dict) and rule.set(data):
                return jsonEncodeFilterByFields(rule, args['fields'])
            
            raise Exception('Invalid request');
