import argparse
import difflib
import re
from pathlib import Path
from typing import List

from bs4 import BeautifulSoup as soup


def main():
    parser = argparse.ArgumentParser(prog="vttdiff")
    parser.add_argument("vtt", nargs="+", help="The path to two (or more) WebVTT files")
    parser.add_argument("--output", help="Write output to this file path")
    parser.add_argument(
        "--ignore-times", action="store_true", help="Ignore cue times in the diff"
    )
    parser.add_argument(
        "--sentences", action="store_true", help="Reorient lines as sentences"
    )
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
        ignore_times=args.ignore_times,
        sentences=args.sentences,
        width=args.width,
    )

    if args.output:
        Path(args.output).open("w").write(html)
    else:
        print(html)


def diff(
    base_vtt: str,
    *target_vtts,
    titles=[],
    ignore_times=False,
    sentences=False,
    width: int = 60,
) -> str:
    """
    Pass in the text of two or more VTT files and get back a string containing the HTML diff.
    The ignore_times option will strip the start/end times from the resulting
    diff. The sentences option will reorient the text so that it contains a
    complete sentence on each line.
    """
    lines1 = lines(base_vtt, ignore_times, sentences)
    lines2 = lines(target_vtts[0], ignore_times, sentences)

    html_diff = difflib.HtmlDiff(wrapcolumn=width)

    html = html_diff.make_file(lines1, lines2, titles[0], titles[1])

    # if more than two vtt files are supplied try to add columns that diff the
    # first vtt against each of the extra ones
    for i, other_vtt in enumerate(target_vtts[1:]):
        html = add_diff(
            html,
            diff(
                base_vtt,
                other_vtt,
                titles=["", titles[i + 2]],
                ignore_times=ignore_times,
                sentences=sentences,
            ),
        )

    return html


def lines(vtt: str, ignore_times: bool, sentences: bool) -> List[str]:
    """
    Pass in WebVTT text and and return a list of just the text lines from the VTT file.
    """
    results = []

    for line in vtt.splitlines():
        if line == "WEBVTT":
            continue
        elif ignore_times and " --> " in line:
            continue
        elif ignore_times and line == "":
            continue
        elif re.match(r"^\d+$", line):
            continue

        results.append(clean(line))

    return split_sentences(results)


sentence_endings = re.compile(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s")


def split_sentences(lines) -> List[str]:
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


def clean(line):
    line = line.replace("<v ->", "")
    line = line.replace("</v>", "")
    return line


def add_diff(html1, html2):
    """
    Add the diff found in html2 as a new set of columns in html1.
    """
    doc1 = soup(html1, "html.parser")
    doc2 = soup(html2, "html.parser")

    existing_rows = doc1.select("table tbody tr")
    new_rows = doc2.select("table tbody tr")

    filename = doc2.body.table.thead.tr.select("th")[3].text
    doc1.body.table.thead.tr.append(
        soup('<th class="diff_next"><br /></th>', "html.parser")
    )
    doc1.body.table.thead.tr.append(
        soup(f'<th class="diff_header" colspan="2">{filename}</th>', "html.parser")
    )

    for i, new_row in enumerate(new_rows):
        existing_rows[i].extend(new_row.select("td")[3:])

    return doc1.prettify()


if __name__ == "__main__":
    main()
