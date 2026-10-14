# Show sliders and menus (ipywidgets). Where the browser cannot draw them, Jupyter
# prints the widget as text ("interactive(children=(Dropdown(...") instead; this
# prints what to do.

from IPython.display import display


def show_controls(controls, by_hand):
    help_text = (
        "[The sliders and menus did not load. Reload the browser tab once (the install cell has "
        "just added the widget library) and run this cell again. Or skip the sliders and type, "
        f"in a new cell: {by_hand}]"
    )
    bundle = getattr(controls, "_repr_mimebundle_", None)
    if bundle is None:  # an older ipywidgets: show it the usual way
        display(controls)
        return
    data = bundle()
    data["text/plain"] = help_text
    display(data, raw=True)
