# coding: utf-8


import pytest
import json
import base64


def test_get_files(core, webapp, webapp_auth_header):

    with webapp.test_client() as c:

        name = 'file1.txt'
        content = u'hello world,  I also accept accents éàç...'

        response = c.post('/api/resources', data=json.dumps({
            'type': 'resources/File',
            'name': name
        }), headers=webapp_auth_header, content_type='application/json')

        data = json.loads(response.data.decode('utf8'))

        print(data)

        assert response.status_code == 201

        assert data['name'] == name

        response = c.put('/api/files/%s' % data['id'],
            data=content.encode('utf8'), headers=webapp_auth_header)

        data = json.loads(response.data.decode('utf8'))

        # size correspond to the byte length
        assert data['size'] == len(content.encode('utf8'))

        response = c.get('/api/files/%s' %
                         data['id'], headers=webapp_auth_header)

        assert response.status_code == 200

        assert response.data.decode('utf8') == content


def test_put_file(core, webapp, webapp_auth_header):

    with webapp.test_client() as c:

        name = 'file1.txt'
        content = u'hello world,  I also accept accents éàç...'

        f = core.create('resources/File', {
            'name': name
        })

        response = c.put('/api/files/%s' % f.id,
                         data=content.encode('utf8'), headers=webapp_auth_header)

        data = json.loads(response.data.decode('utf8'))

        print(data)

        assert response.status_code == 200

        assert data['name'] == name

        # size correspond to the byte length
        assert data['size'] == len(content.encode('utf8'))

        response = c.get('/api/files/%s' % f.id, headers=webapp_auth_header)

        assert response.status_code == 200

        assert response.data.decode('utf8') == content

