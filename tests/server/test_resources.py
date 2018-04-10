# coding: utf-8
import pytest
import json


def test_get_resources(core, webapp, webapp_auth_header):
    
    
    content = b'hello world'
    
    def create_file():
        f = core.create('File', {
            'name' : 'file1.txt'
        })
        
        f.write(content)
    
    count = 3
    for _ in range(0,count):
        create_file()
    
    with webapp.test_client() as c:
        response = c.get('/api/resources', headers=webapp_auth_header)
        
        data = json.loads(response.data.decode())
        
        print(data)
        
        assert response.status_code == 200
        
        assert isinstance(data, list)
        
        assert len(data) == count
    