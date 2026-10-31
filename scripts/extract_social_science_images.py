"""Extract the user's worksheet pictures without adjacent answer labels.

Coordinates use a 1200x900 upright reference. Originals remain untouched.
Requires Pillow; run with --source-dir pointing to the supplied WhatsApp photos.
"""
import argparse
from pathlib import Path
from PIL import Image, ImageOps

ASSETS = Path(__file__).with_name('social_science_assets') / 'images'
SHEETS = {
    'school': ('09.45.42 (3)', 90),
    'workers': ('09.45.42 (2)', 90),
    'helpers': ('09.45.43', 90),
    'places': ('09.45.43 (1)', 270),
    'family': ('09.45.42', 90),
}
# Tight bounds exclude printed vocabulary, handwriting and correction marks.
CROPS = {
    'classroom': ('school', (44,337,213,443)),
    'library': ('school', (255,334,425,442)),
    'canteen': ('school', (471,331,655,443)),
    'lab': ('school', (711,329,886,438)),
    'gym': ('school', (945,325,1135,443)),
    'playground': ('school', (43,521,208,630)),
    'reception': ('school', (252,520,432,637)),
    'toilets': ('school', (483,540,676,632)),
    'art-room': ('school', (715,513,891,640)),
    'nurse-office': ('school', (961,515,1141,640)),
    'teacher': ('workers', (197,365,277,439)),
    'headmaster': ('workers', (199,448,273,532)),
    'school-nurse': ('workers', (207,546,266,637)),
    'cook': ('workers', (189,660,278,737)),
    'caretaker': ('workers', (609,345,698,425)),
    'cleaner': ('workers', (609,432,703,543)),
    'receptionist': ('workers', (616,558,706,634)),
    'librarian': ('workers', (623,652,706,735)),
    'mayor': ('helpers', (373,308,492,405)),
    'doctor': ('helpers', (560,307,658,432)),
    'gardener': ('helpers', (720,300,837,432)),
    'firefighter': ('helpers', (384,453,484,581)),
    'police-officer': ('helpers', (562,453,661,581)),
    'bus-driver': ('helpers', (310,610,449,754)),
    'postman': ('helpers', (479,606,584,747)),
    'street-cleaner': ('helpers', (611,604,747,747)),
    'neighbourhood': ('places', (140,431,374,648)),
    'city': ('places', (393,412,615,642)),
    'village': ('places', (632,401,856,640)),
    'town': ('places', (881,401,1107,630)),
    # A neutral family group: no handwritten labels or highlighted target person.
    'family': ('family', (613,352,810,642)),
}


def extract(source_dir, output_dir=ASSETS):
    output_dir.mkdir(parents=True, exist_ok=True)
    sheets = {}
    for key, (time, rotation) in SHEETS.items():
        source = source_dir / f'WhatsApp Image 2026-10-31 at {time}.jpeg'
        with Image.open(source) as photo:
            sheets[key] = ImageOps.exif_transpose(photo).convert('RGB').rotate(rotation, expand=True)
    for key, (sheet, bounds) in CROPS.items():
        image = sheets[sheet]
        coords = tuple(round(v * (image.width / 1200 if i % 2 == 0 else image.height / 900))
                       for i, v in enumerate(bounds))
        crop = image.crop(coords)
        crop.thumbnail((600, 480), Image.Resampling.LANCZOS)
        crop.save(output_dir / f'social-oct26-{key}.jpg', quality=92)
    return len(CROPS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, default=ASSETS)
    args = parser.parse_args()
    print(f'Extracted {extract(args.source_dir, args.output_dir)} original worksheet pictures.')


if __name__ == '__main__':
    main()
