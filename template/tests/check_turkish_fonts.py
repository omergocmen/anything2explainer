"""Optional font coverage check: pip install fonttools; python tests/check_turkish_fonts.py."""
from pathlib import Path
from fontTools.ttLib import TTFont

fonts = Path(__file__).resolve().parents[1] / 'public/fonts'
letters = 'ÇĞIİÖŞÜçğıiöşü'
for filename in ('NotoSans.ttf', 'Audiowide-Regular.ttf', 'Exo2-Italic.ttf'):
    with TTFont(fonts / filename) as font:
        cmap = font.getBestCmap()
        missing = [letter for letter in letters if ord(letter) not in cmap]
        assert not missing, f'{filename} lacks {missing}'
    print(f'{filename}: Turkish glyph coverage OK')
