import vttdiff

import pytest


@pytest.fixture
def vtt1():
    return open("test/data/vtt1.vtt").read()


@pytest.fixture
def vtt2():
    return open("test/data/vtt2.vtt").read()


@pytest.fixture
def vtt3():
    return open("test/data/vtt3.vtt").read()


def test_two(vtt1, vtt2):
    html = vttdiff.diff(vtt1, vtt2, titles=["vtt1", "vtt2"])
    assert html


def test_three(vtt1, vtt2, vtt3):
    html = vttdiff.diff(vtt1, vtt2, vtt3, titles=["vtt1", "vtt2", "vtt3"])
    assert html


def test_sentences():
    lines = ["To be or not to be. That is the question. What's that a", "burrito?"]
    assert vttdiff.split_sentences(lines) == [
        "To be or not to be.",
        "That is the question.",
        "What's that a burrito?",
    ]
