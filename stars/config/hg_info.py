from mercurial import ui, hg
import os, sys

try:
    repo = hg.repository(ui.ui(), os.path.join(os.path.dirname(__file__), '../..'))
    parent = repo.parents()[0]

    revision = "r%s:%s" % (parent.rev(), parent.hex()[:12])
except:
    revision = None

# print >> sys.stderr, "REVISION: %s" % revision