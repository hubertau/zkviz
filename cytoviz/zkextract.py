"""

Visualize the notes network of a Zettelkasten.

Each arrow represents a link from one zettel to another. The script assumes
that zettels have filenames of the form "YYYYMMDDHHMM This is a title" and that
links have the form [[YYYYMMDDHHMM]]

"""
import glob
import os.path
import re
from textwrap import fill


PAT_ZK_ID = re.compile(r"^(?P<id>\d+)\s(.*)")
PAT_LINK = re.compile(r"\[\[(\d+)\]\]")


def parse_zettels(filepaths):
    """ Parse the ID and title from the filename and first line of the file.

    Assumes that the filename has the format "This is title" and the first line
    of the file is the ID

    """
    documents = {}
    for filepath in filepaths:
        basename = os.path.basename(filepath)
        filename, ext = os.path.splitext(basename)

        # collect zkn_id
        with open(filepath, encoding="utf-8") as f:
            # read file
            file_read = f.read()

            # search for the first string of 14 digits with arbitrary
            # non-digits on either side.
            zkn_id = re.search('\d{14}', file_read)

            zkn_id = zkn_id.group(0)

            # collect links
            links = PAT_LINK.findall(file_read)


        # now collect text
        with open(filepath, encoding='utf-8') as f:
            f.readline()
            doctext = f.readlines()

        # document = dict(id=r.group(1), title=r.group(2), links=links)
        # document = dict(id = zkn_id, title = filename, links = links, text = doctext)
        # documents.append(document)
        documents[zkn_id] = dict(title = filename, links = links, text = doctext)

    return documents


def create_graph(zettels, include_self_references=True, only_listed=True):
    """
    Create of graph of the zettels linking to each other.

    Parameters
    ----------
    zettels : list of dictionaries
    include_self_references : bool, optional
        Include links to the source document. Defaults to True.
    only_listed : bool, optional
        Only include nodes in the graph it's actually one of the zettels.
        Default is False.

    Returns
    -------
    graph : cytoscape-compatible set of elements

    """

    # Collect IDs from source zettels and from zettels linked
    zettel_ids = set()
    link_ids = set()
    for zettel in zettels:
        zettel_ids.add(zettel["id"])
        link_ids.update(zettel["links"])

    if only_listed:
        ids_to_include = zettel_ids
    else:
        ids_to_include = zettel_ids | link_ids

    # for zettel in zettels:
    #     graph.add_node(zettel["id"], title=zettel["title"])
    #     for link in zettel["links"]:
    #         if link not in ids_to_include:
    #             continue
    #         if include_self_references or (zettel["id"] != link):
    #             # Truth table for the inclusion conditional
    #             #               IS_SAME IS_DIFF   (Is different ID)
    #             # INCLUDE          T       T
    #             # DON'T INCLUDE    F       T
    #             graph.add_edge(zettel["id"], link)

    elements = []
    for zettel in zettels:

        # add node
        elements.append({
            'data': {'id': zettel['id'], 'label': zettel['title']}
        })

        # add link_ids
        for link in zettel["links"]:
            if link not in ids_to_include:
                continue
            if include_self_references or (zettel["id"] != link):
                # Truth table for the inclusion conditional
                #               IS_SAME IS_DIFF   (Is different ID)
                # INCLUDE          T       T
                # DON'T INCLUDE    F       T
                elements.append({
                    'data': {'source': zettel['id'], 'target': link}
                })

    return elements


def list_zettels(notes_dir, pattern="*.md"):
    """
    List zettels in a directory.

    Parameters
    ----------
    notes_dir : str
        Path to the directory containing the zettels.
    pattern : str (optional)
        Pattern matching zettels. The default is '*.md'. If there are multiple
        patterns, separate them with a |, such as in '*.md|*.txt'

    """

    filepaths = []

    for patt in pattern.split("|"):
        filepaths.extend(glob.glob(os.path.join(notes_dir, patt)))
    return sorted(filepaths)


def parse_args(args=None):
    from argparse import ArgumentParser

    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--notes-dir", default=".", help="path to folder containin notes. [.]"
    )
    parser.add_argument(
        "--output",
        default="zettel-network",
        help="name of output file. [zettel-network]",
    )
    parser.add_argument(
        "--pattern",
        action="append",
        help=(
            "pattern to match notes. You can repeat this argument to"
            " match multiple file types. [*.md]"
        ),
    )
    parser.add_argument(
        "--use-graphviz",
        action="store_true",
        default=False,
        help="Use Graphviz instead of plotly to render the network.",
    )
    parser.add_argument(
        "--no-self-ref",
        action="store_false",
        default=True,
        dest="include_self_references",
        help="Do not include self-references in a zettel.",
    )
    parser.add_argument(
        "--only-listed",
        action="store_true",
        default=False,
        help="Only include links to documents that are in the file list",
    )
    parser.add_argument("zettel_paths", nargs="*", help="zettel file paths.")
    args = parser.parse_args(args=args)

    # Use the list of files the user specify, otherwise, fall back to
    # listing a directory.
    if not args.zettel_paths:
        if args.pattern is None:
            args.pattern = ["*.md"]
        patterns = "|".join(args.pattern)

        args.zettel_paths = list_zettels(args.notes_dir, pattern=patterns)
    return args


def main(args=None):
    args = parse_args(args)

    zettels = parse_zettels(args.zettel_paths)

    # Fail in case we didn't find a zettel
    if not zettels:
        raise FileNotFoundError("I'm sorry, I couldn't find any files.")

    graph = create_graph(
        zettels,
        graph,
        include_self_references=args.include_self_references,
        only_listed=args.only_listed,
    )

if __name__ == "__main__":
    import sys

    try:
        sys.exit(main())
    except FileNotFoundError as e:
        # Failed either because it didn't find any files or because Graphviz
        # wasn't installed
        sys.exit(e)
