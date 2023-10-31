from typing import Union, List

import IPython


def display(color: Union[str, List[str]], inline: bool = False, **kwargs):
    """Generate a badge from a key-value pair, e.g. display_as_badge(winsize=64).
    If multiple key-value pairs are given but not enough colors, the default color is
    lightgray.
    """
    _shield_strings = []
    colors = ['lightgray'] * len(kwargs)
    if isinstance(color, str):
        colors[0] = color
    else:
        colors[0:len(color)] = color

    for (k, v), color in zip(kwargs.items(), colors):
        _str = f'{v}'.replace(' ', '_').replace('-', '--')
        if '%' in _str:
            _str = _str.replace('%', '%25')
        badge_str = f'![nbviewer](https://img.shields.io/badge/{k}-{_str}-{color}.svg)'
        if isinstance(v, str):
            if v.startswith('https://') or v.startswith('www.'):
                badge_str = f'[{badge_str}]({v})'
        _shield_strings.append(badge_str)
    if inline:
        return IPython.display.Markdown(' '.join(_shield_strings))
    IPython.display.display(IPython.display.Markdown('<br>'.join(_shield_strings)))
