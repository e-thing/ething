# coding: utf-8
import pytest
import json


def test_get_resources(core, webapp, webapp_auth_header):

    content = b'hello world'

    before_count = len(core.find())

    def create_file():
        f = core.create('resources/File', {
            'name': 'file1.txt'
        })

        f.write(content)

    count = 3
    for _ in range(count):
        create_file()

    with webapp.test_client() as c:
        response = c.get('/api/resources', headers=webapp_auth_header)

        data = json.loads(response.data.decode())

        print(data)

        assert response.status_code == 200

        assert isinstance(data, list)

        assert len(data) == before_count + count
