import jinja2

import jinja2_pdoc


def test_environment():
    assert issubclass(jinja2_pdoc.Environment, jinja2.Environment)


def test_env():
    env = jinja2_pdoc.Environment()

    assert isinstance(env, jinja2.Environment)


def test_preloaded():
    env = jinja2_pdoc.Environment()

    assert "jinja2_pdoc.extension.Jinja2Pdoc" in env.extensions.keys()
