# Poppins web fonts

These WOFF files contain the complete Poppins Regular and Poppins SemiBold fonts, losslessly packaged from the corresponding local TTF files. The SVG renderer embeds them as data URIs at CSS weights 400 and 600.

Poppins is distributed under the [SIL Open Font License 1.1](./OFL.txt). The license and copyright notice were verified against the [Poppins license in Google Fonts](https://github.com/google/fonts/blob/main/ofl/poppins/OFL.txt). Original font metadata is preserved in each WOFF file.

To regenerate from licensed source fonts, run `python scripts/prepare_fonts.py path/to/Poppins-Regular.ttf path/to/Poppins-SemiBold.ttf` from the repository root. The utility follows [WOFF 1.0](https://www.w3.org/TR/WOFF/), preserves the original table order and glyph data, and validates byte-exact round-trip decoding plus the SFNT and individual table checksums.
