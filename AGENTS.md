# Coral agent guidance

For any task that writes the knowledge wiki, read `wiki/_index.md` first and treat it as the canonical editorial and evidence contract. Do not duplicate that contract here.

Before finishing a wiki-writing task:

1. Perform the synthesis-impact check required by `_index.md`; update synthesis only for a material causal, evidentiary, practical, safety, or uncertainty change.
2. Preserve corrections and provenance rather than silently overwriting formerly supported conclusions.
3. Keep concept chapters in their primary subject-area subfolder and preserve stem-based wikilinks.
4. Run `uv run python update_wiki.py --validate-wiki` after structural or citation changes.
