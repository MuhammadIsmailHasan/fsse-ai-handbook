"""Checks for helm_render.py. Don't edit this file."""

import pytest

from helm_render import render


def test_single_blank():
    assert render("replicas: {{ .Values.replicas }}", {"replicas": 3}) == "replicas: 3"


def test_multiple_blanks_and_repeats():
    template = "name: {{ .Values.name }}\nimage: {{ .Values.name }}:{{ .Values.tag }}"
    out = render(template, {"name": "revoshop", "tag": "v1.4"})
    assert out == "name: revoshop\nimage: revoshop:v1.4"


def test_flexible_spacing():
    assert render("a: {{.Values.x}} b: {{   .Values.x   }}", {"x": 7}) == "a: 7 b: 7"


def test_no_blanks_unchanged():
    assert render("plain: yaml", {}) == "plain: yaml"


def test_missing_key_raises():
    with pytest.raises(KeyError):
        render("{{ .Values.missing }}", {"present": 1})


def test_integer_value_becomes_string():
    assert render("{{ .Values.n }}", {"n": 0}) == "0"
