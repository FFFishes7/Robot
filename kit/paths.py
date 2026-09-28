"""Repository locations for the build scripts; everything the build reads or writes lives inside the repository.
ROOT = repository root, KIT = kit/, BUILD = build/ (renders and intermediates, git-ignored). All end with '/'."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/") + "/"
KIT = ROOT + "kit/"
BUILD = ROOT + "build/"
