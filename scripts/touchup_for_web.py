#!/usr/bin/python
#
# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Post-build web fonts changes for Roboto."""

import sys

from fontTools import ttLib
from nototools import font_data

import temporary_touchups


def apply_web_specific_fixes(font, family_name):
    """Apply fixes needed for web fonts."""
    # Set OS/2 table values to old values
    os2 = font['OS/2']
    os2.sTypoAscender = 1536
    os2.sTypoDescender = -512
    os2.sTypoLineGap = 102
    os2.usWinAscent = 1946
    os2.usWinDescent = 512

    subfamily_name = font_data.get_name_records(font)[2].encode('ASCII')
    assert(subfamily_name in
        ['Thin', 'Thin Italic',
         'Light', 'Light Italic',
         'Regular', 'Italic',
         'Medium', 'Medium Italic',
         'Bold', 'Bold Italic',
         'Black', 'Black Italic'])

    if 'Condensed' in font_data.get_name_records(font)[1]:
        family_name += ' Condensed'
    full_name = family_name
    if subfamily_name != 'Regular':
        full_name += ' ' + subfamily_name

    # Family, subfamily names
    font_data.set_name_record(font, 16, family_name)
    style_map = ['Regular', 'Bold', 'Italic', 'Bold Italic']
    if subfamily_name in style_map:
        font_data.set_name_record(font, 1, family_name)
    else:
        weight = subfamily_name.split()[0]
        new_family_name = family_name
        if weight != 'Regular':
            new_family_name += ' ' + weight
        font_data.set_name_record(font, 1, new_family_name)

        # all weights outside regular and bold should only have subfamily
        # "Regular" or "Italic"
        italic = subfamily_name.endswith('Italic')
        font_data.set_name_record(font, 2, style_map[italic << 1])

    # Unique identifier and full name
    font_data.set_name_record(font, 3, full_name)
    font_data.set_name_record(font, 4, full_name)
    font_data.set_name_record(font, 18, None)

    # PostScript name
    font_data.set_name_record(
        font, 6, (family_name+'-'+subfamily_name).replace(' ', ''))

    # Copyright message
    font_data.set_name_record(
        font, 0, 'Copyright 2011 Google Inc. All Rights Reserved.')


def correct_font(source_font_name, target_font_name, family_name):
    """Corrects metrics and other meta information."""
    font = ttLib.TTFont(source_font_name)
    temporary_touchups.apply_temporary_fixes(font)
    apply_web_specific_fixes(font, family_name)
    font.save(target_font_name)


def main(argv):
    """Correct the font specified in the command line."""
    correct_font(argv[1], argv[2], argv[3])


if __name__ == "__main__":
    main(sys.argv)
