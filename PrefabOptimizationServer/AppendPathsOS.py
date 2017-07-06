import os
import sys

def CheckAppendPath(*dirs):
    path = os.path.join(*dirs)
    path = os.path.normpath(path)   # collapsing ".."
    if not path in sys.path:
        sys.path.append(path)

def AppendPathsOS(testMode=False):
    """Append all paths used in this project to the system paths list"""

    dir = os.path.dirname(os.path.abspath(__file__))

    # This project
    CheckAppendPath(dir, "NLPDataProcessing")

    # Dependency project
    CheckAppendPath(dir, "..", "..", "PrefabCommon", "PrefabCommon")