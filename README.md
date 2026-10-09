# SSRQ Utils

Various utilities for the SSRQ project e.g. for parsing IDNOs or handling `urn:ssrq`-strings.

## Installation

This project uses `uv` for dependency managment and `just` for running tasks (defined as dev dependency). After installing everything (`uv sync --all-extras --dev`) run `just help` to see available tasks.

## Authors

- [Bastian Politycki](https://github.com/Bpolitycki) – Swiss Law Sources

## Contextual translation prefixes

Use `translator.translate_before(lang, key, following)` to translate a prefix
and join it directly to the following text. The returned string includes the
separator: `avec la collaboration de Bernard`, but `avec la collaboration d’Anna`.

Provide an optional `<key>_elided` entry in the translation JSON. French selects
this variant before vowel-initial full names, including accented vowels and y.
Initials such as `A. Dupont` keep the ordinary form. An elided variant ending in
`’` or `'` joins without a space; other prefixes use one space. The existing
`translate` method is unchanged.

For names whose pronunciation cannot be inferred from spelling, pass
`elide=True` (e.g. a mute h in `Henri`) or `elide=False` (e.g. an aspirated h).
Names beginning with h default to no elision. Overrides only affect French and
only select an existing variant; they do not rewrite translated strings.

The translation model requires equal counts of ordinary entries across all four
languages. Optional keys ending in `_elided` are excluded from this check, so
French variants can be defined only in `fr`. They remain available for lookup
and cannot compensate for missing ordinary translations.
