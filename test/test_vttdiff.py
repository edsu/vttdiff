import vttdiff

from bs4 import BeautifulSoup as soup
from pytest import fixture


@fixture
def vtt1() -> str:
    return open("test/data/vtt1.vtt").read()


@fixture
def vtt2() -> str:
    return open("test/data/vtt2.vtt").read()


@fixture
def vtt3() -> str:
    return open("test/data/vtt3.vtt").read()


def test_two(vtt1, vtt2) -> None:
    html = vttdiff.diff(vtt1, vtt2, titles=["vtt1", "vtt2"])
    assert html


def test_three(vtt1, vtt2, vtt3) -> None:
    html = vttdiff.diff(vtt1, vtt2, vtt3, titles=["vtt1", "vtt2", "vtt3"])
    assert html


def test_sentences() -> None:
    lines = ["To be or not to be. That is the question. What's that a", "burrito?"]
    assert vttdiff.split_sentences(lines) == [
        "To be or not to be.",
        "That is the question.",
        "What's that a burrito?",
    ]


def test_stats_html(vtt1, vtt2) -> None:
    html = vttdiff.diff(vtt1, vtt2, titles=["vtt1", "vtt2"])
    doc = soup(html, "html.parser")

    wer = doc.select(".stats .wer td")[1]
    assert wer, "found stats wer"
    assert wer.text.strip() == "0.09043421482206987"
