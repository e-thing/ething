# coding: utf-8
import pytest
from ething.ScriptEngine import ScriptEngine


@pytest.mark.nodejs
def test_scriptengine(core):

    result = ScriptEngine.run(core, 'console.log("toto")')

    assert result.get('ok') is True


@pytest.mark.nodejs
def test_scriptengine_script(core):

    script_content = u'script instanceof EThing.Resource ? 1 : 0'

    script = core.create('resources/File', {
        'name': 'script.js'
    })

    script.write(script_content, encoding='utf8')

    result = ScriptEngine.runFromFile(script)

    print(result.get('stderr'))

    assert result.get('ok') is True


@pytest.mark.nodejs
def test_scriptengine_script_arg(core):

    script_content = u'argv.length'

    script = core.create('resources/File', {
        'name': 'script.js'
    })

    script.write(script_content, encoding='utf8')

    result = ScriptEngine.runFromFile(script, arguments='foo "bar fg"')

    print(result.get('stderr'))

    assert result.get('ok') is True
