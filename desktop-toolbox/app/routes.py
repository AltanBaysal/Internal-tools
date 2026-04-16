"""Single source of truth for the modules the shell mounts.

Adding a module: import its `module_spec` and append it to MODULES. Done.
"""

from modules.frame_extractor import module_spec as frame_extractor

MODULES = [
    frame_extractor,
]

ROUTES = {m.route: m for m in MODULES}
