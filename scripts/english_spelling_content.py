"""Vocabulary transcribed from the supplied Unit 1 photo and Unit 2 PDF."""
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Vocabulary:
    unit: int
    answer: str
    tile: int
    weekday: int = 0

    @property
    def key(self):
        return f"u{self.unit}-" + re.sub(r'[^a-z0-9]+', '-', self.answer.lower()).strip('-')

    @property
    def audio_filename(self):
        return f"english-spelling-{self.key}.mp3"


_UNIT1 = (
    'field', 'forest', 'grass', 'lake', 'mountain', 'river', 'leaf', 'leaves',
    'rock', 'to have breakfast', 'to wash your hands', 'to drink water',
    'to have a shower', 'towel', 'toothbrush', 'toothpaste',
)
_DAYS = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
_UNIT2_ACTIONS = (
    'to listen to music', 'to write an email', 'to go skating', 'to read a comic',
    'to go shopping', 'to watch films', 'must', "mustn't",
)
ITEMS = tuple(Vocabulary(1, word, i) for i, word in enumerate(_UNIT1)) + tuple(
    Vocabulary(2, day, 0, i + 1) for i, day in enumerate(_DAYS)
) + tuple(Vocabulary(2, word, i + 1) for i, word in enumerate(_UNIT2_ACTIONS))


def completion_masks(answer):
    """Three distinct, complementary patterns; every letter is recalled once.

    Split each word into three near-equal contiguous pieces. The early pattern
    hides the middle piece, then the end, then the beginning. Spaces and the
    apostrophe remain visible. Short function words contribute one letter to
    each of the first two patterns.
    """
    masks = [[], [], []]
    for match in re.finditer(r'[A-Za-z]+', answer):
        positions = list(range(match.start(), match.end()))
        if len(positions) < 3:
            for i, pos in enumerate(positions):
                masks[i].append(pos)
            continue
        size, remainder = divmod(len(positions), 3)
        widths = [size + (i < remainder) for i in range(3)]
        cursor = 0
        for part, width in enumerate(widths):
            masks[(part + 2) % 3].extend(positions[cursor:cursor + width])
            cursor += width
    return [sorted(mask) for mask in masks]


def picture_html(item):
    """Render a cell of the generated atlas without altering its bitmap.

    A genuine img reference keeps Anki's media checker/sync aware of the atlas.
    The wrapper clips the atlas to the chosen cell; source labels never appear.
    """
    columns = 4 if item.unit == 1 else 3
    row, col = divmod(item.tile, columns)
    markup = (
        '<div><div style="position:relative;width:190px;height:190px;overflow:hidden;'
        'margin:0 auto;background:white;border-radius:20px">'
        f'<img src="english-spelling-unit{item.unit}.png" alt="Vocabulary illustration" '
        f'style="position:absolute;width:{columns * 100}%;height:{columns * 100}%;'
        f'max-width:none;max-height:none;object-fit:fill;border-radius:0;left:-{col * 100}%;top:-{row * 100}%;pointer-events:none">'
        '</div>'
    )
    if item.weekday:
        dots = ''.join(
            '<span style="display:inline-block;width:10px;height:10px;border-radius:50%;'
            f'background:{"#23796d" if day == item.weekday else "#dce8e4"}"></span>'
            for day in range(1, 8)
        )
        markup += f'<div aria-hidden="true" style="display:flex;justify-content:center;gap:8px;margin:8px">{dots}</div>'
    return markup + '</div>'
