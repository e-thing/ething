# coding: utf-8
import pytest


def test_get_files(core, webapp):

    with webapp.test_client() as c:
        name = 'file1.txt'
        content = u'hello world'
        content2 = u'foobar'

        f = core.create('resources/File', {
            'name': name
        })

        f.write(content, encoding='utf8')

        response = c.get('/api/files/%s' % f.id)
        assert response.status_code == 401

        response = c.put('/api/files/%s' % f.id, data=content2.encode('utf8'))
        assert response.status_code == 401

        f.public = 'readonly'

        response = c.get('/api/files/%s' % f.id)
        print(response.data)
        assert response.status_code == 200
        assert response.data.decode('utf8') == content

        response = c.put('/api/files/%s' % f.id, data=content2.encode('utf8'))
        assert response.status_code == 403

        f.public = 'readwrite'

        response = c.get('/api/files/%s' % f.id)
        assert response.status_code == 200
        assert response.data.decode('utf8') == content

        response = c.put('/api/files/%s' % f.id, data=content2.encode('utf8'))
        assert response.status_code == 200


