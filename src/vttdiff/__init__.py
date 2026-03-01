import argparse
import difflib
import re
import string
from pathlib import Path
from typing import List

import bs4
import jiwer
from bs4 import BeautifulSoup as soup


def main():
    parser = argparse.ArgumentParser(prog="vttdiff")
    parser.add_argument("vtt", nargs="+", help="The path to two (or more) WebVTT files")
    parser.add_argument("--output", help="Write output to this file path")
    parser.add_argument(
        "--width",
        type=int,
        default=60,
        help="The default width (in characters) of each transcript in the diff",
    )
    args = parser.parse_args()

    if len(args.vtt) < 2:
        parser.error("Please supply two or more WebVTT files")

    vtts = []
    titles = []
    for path in args.vtt:
        vtt = Path(path)
        if not vtt.is_file():
            parser.error(f"No such file {path}")
        vtts.append(vtt.open().read())
        titles.append(vtt.name)

    html = diff(
        *vtts,
        titles=titles,
        width=args.width,
    )

    if args.output:
        Path(args.output).open("w").write(html)
    else:
        print(html)


def diff(
    base_vtt: str,
    *target_vtts: str,
    titles: list[str]=[],
    width: int = 60,
) -> str:
    """
    Pass in the text of two or more VTT files and get back a string containing the HTML diff.
    """
    lines1 = lines(base_vtt)
    lines2 = lines(target_vtts[0])

    # create the initial diff
    html_diff = difflib.HtmlDiff(wrapcolumn=width)
    html = html_diff.make_file(lines1, lines2, titles[0], titles[1])

    # add any additional diffs for when there are more than two vtts
    for i, other_vtt in enumerate(target_vtts[1:]):
        html = add_diff(
            html,
            diff(
                base_vtt,
                other_vtt,
                titles=["", titles[i + 2]],
            ),
        )

    html = add_stats(html, base_vtt, target_vtts, titles)

    return html


def lines(vtt: str) -> List[str]:
    """
    Pass in WebVTT text and and return a list of just the text lines from the VTT file.
    """
    results = []

    for line in vtt.splitlines():
        if line == "WEBVTT":
            continue
        elif " --> " in line:
            continue
        elif line == "":
            continue
        elif re.match(r"^\d+$", line):
            continue

        results.append(clean(line))

    return split_sentences(results)


sentence_endings = re.compile(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s")


def split_sentences(lines: List[str]) -> List[str]:
    """
    Split lines with multiple sentences into multiple lines. So,

        To be or not to be. That is the question. What's that a
        burrito?

    will become:

        To be or not to be.
        That is the question.
        What's that a burrito?
    """
    text = " ".join(lines)
    text = text.replace("\n", " ")
    text = re.sub(r" +", " ", text)
    sentences = sentence_endings.split(text.strip())
    sentences = [sentence.strip() for sentence in sentences]

    return sentences


def clean(line: str) -> str:
    line = line.replace("<v ->", "")
    line = line.replace("</v>", "")
    return line


def jiwer_text(lines: list[str]) -> str:
    """
    Normalize lines of text for jiwer analysis.
    """
    text = " ".join(lines)
    text = text.replace("\n", " ")
    text = re.sub(r"  +", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = text.lower()
    text = text.strip()
    return text


def add_diff(html1: str, html2: str) -> str:
    """
    Add the diff found in html2 as a new set of columns in html1.
    """
    doc1 = soup(html1, "html.parser")
    doc2 = soup(html2, "html.parser")

    existing_rows = doc1.select("table tbody tr")
    new_rows = doc2.select("table tbody tr")

    filename = doc2.select("body table thead tr th")[3].text

    tr = doc1.select("body table thead tr")
    tr.append(soup('<th class="diff_next"><br /></th>', "html.parser"))
    tr.append(soup(f'<th class="diff_header" colspan="2">{filename}</th>', "html.parser"))

    for i, new_row in enumerate(new_rows):
        if i < len(existing_rows):
            existing_rows[i].extend(new_row.select("td")[3:])

    return str(doc1.prettify())


def add_stats(
    html: str, base_vtt: str, target_vtts: tuple[str, ...], titles: list[str]
) -> str:
    """
    Add comparison statistics to the supplied HTML document.
    """

    doc = soup(html, "html.parser")
    base_text = jiwer_text(lines(base_vtt))
    base_title = titles[0]

    for i, other_vtt in enumerate(target_vtts):
        other_text = jiwer_text(lines(other_vtt))
        other_title = titles[i + 1]

        stats = jiwer.process_words(base_text, other_text)

        table = soup(
            f"""
            <table class="stats" style="border: thin solid; margin-top: 20px; min-width: 500px;">
              <thead><th colspan="2" style="border-bottom: thin solid;">Comparing {base_title} to {other_title}</th></thead>
              <tr class="wer"><tr><td>Word Error Rate</td><td align="right">{stats.wer}</td></tr>
              <tr class="mer"><tr><td>Match Error Rate</td><td align="right">{stats.mer}</td></tr>
              <tr class="wil"><tr><td>Word Information Loss</td><td align="right">{stats.wil}</td></tr>
              <tr class="wip"><tr><td>Word Information Preserved</td><td align="right">{stats.wip}</td></tr>
              <tr class="hits"><tr><td>Correct Words</td><td align="right">{stats.hits}</td></tr>
              <tr class="substitutions"><tr><td>Substitions</td><td align="right">{stats.substitutions}</td></tr>
              <tr class="insertions"><tr><td>Insertions</td><td align="right">{stats.insertions}</td></tr>
              <tr class="deletions"><tr><td>Deletions</td><td align="right">{stats.deletions}</td></tr>
            </table>
            """,
            "html.parser",
        )

        if doc.body:
            doc.body.append(table)
        else:
            raise Exception("Unable to find body of HTML document!")

    return str(doc.prettify())


if __name__ == "__main__":
    main()
