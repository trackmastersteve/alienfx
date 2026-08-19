from __future__ import absolute_import


def start(*args, **kwargs):
	from alienfx.ui.gtkui.gtkui import start as gtkui_start

	return gtkui_start(*args, **kwargs)


# start()  # debug (needed for debugging in pycharm)
