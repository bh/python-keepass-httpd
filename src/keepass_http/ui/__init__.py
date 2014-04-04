from keepass_http.utils import has_gui_support

import cli

if has_gui_support():  # pragma: no cover
    import gui
