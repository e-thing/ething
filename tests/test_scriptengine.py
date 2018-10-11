# coding: utf-8
import pytest
from ething.plugins.JsScript import JsScript


@pytest.mark.nodejs
def test_scriptengine(core):
    js = JsScript(core)
    result = js.run('console.log("toto")')

    assert result.get('ok') is True


@pytest.mark.nodejs
def test_scriptengine_script(core):
    js = JsScript(core)

    script_content = u'script instanceof EThing.Resource ? 1 : 0'

    script = core.create('resources/File', {
        'name': 'script.js'
    })

    script.write(script_content, encoding='utf8')

    result = js.runFromFile(script)

    print(result.get('stderr'))

    assert result.get('ok') is True


@pytest.mark.nodejs
def test_scriptengine_script_arg(core):
    js = JsScript(core)

    script_content = u'argv.length'

    script = core.create('resources/File', {
        'name': 'script.js'
    })

    script.write(script_content, encoding='utf8')

    result = js.runFromFile(script, arguments='foo "bar fg"')

    print(result.get('stderr'))

    assert result.get('ok') is True
