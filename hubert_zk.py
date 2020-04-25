from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from zkviz import zkviz

# zkviz.main(["--use-graphviz", "--notes-dir", "/Users/hubert/Nextcloud/Zettelkasten"])
zkviz.main(["--notes-dir", "/Users/hubert/Nextcloud/Zettelkasten"])
