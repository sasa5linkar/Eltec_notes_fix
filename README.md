# TEI Endnote Inlining Transformation

This project provides a Python script for transforming TEI P5 XML documents by converting ELTeC-style endnotes into inline notes suitable for TEI Publisher rendering.

## Overview

The script performs an **endnote inlining transformation** on TEI XML documents:

- **Source encoding**: Endnotes stored in `<back><div type="notes">` as `<note xml:id="…">`, referenced from running text via `<ref target="#NOTE_ID"/>` elements
- **Target encoding**: Notes inlined in the running text as `<note place="inline">…</note>` at the exact position of the former `<ref>`

## Requirements

- Python 3.8 or higher
- lxml library (for XML processing)

## Installation

### Option 1: Using the Windows Batch File (Recommended for Windows)

Simply run the provided batch file which will:
1. Create a virtual environment
2. Install dependencies
3. Run the transformation
4. Write a run log (`Output\\run.log`) and per-file summary table (`Output\\run_summary.csv`)

```batch
setup_and_run.bat
```

### Option 2: Manual Installation

1. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python inline_notes.py <input_folder> <output_folder>
```

### Example

```bash
python inline_notes.py Input Output
```

This will:
- Process all XML files in the `Input` folder
- Save transformed files to the `Output` folder (created automatically if it doesn't exist)
- Preserve original filenames

## Transformation Rules

### 1. Endnote Identification

- Only treats `<note>` elements inside `<back><div type="notes">` as endnotes
- Ignores all other `<note>` elements (e.g., editorial notes already inline, notes in header)

### 2. Reference Identification

Only replaces `<ref>` elements that:
- Have a `@target` attribute starting with `#`
- Point to an existing endnote `xml:id` in `<back><div type="notes">`

Does NOT touch `<ref>` elements that:
- Point to external URLs
- Point to internal targets outside the notes div
- Appear inside `<teiHeader>`

### 3. Inlining Behavior

- Replaces each qualifying `<ref target="#NOTE_ID"/>` with `<note place="inline">NOTE_CONTENT</note>`
- NOTE_CONTENT includes full mixed content (text and inline markup like `<hi>`, `<foreign>`, etc.)
- Does NOT copy the `xml:id` to the inline note
- Does NOT add numbering or brackets unless already present

### 4. Multiple References

- If the same endnote is referenced multiple times, it's inlined independently at each reference point
- Content is duplicated as expected

### 5. Cleanup

After successful inlining:
- Removes the entire `<div type="notes">` from `<back>`
- If `<back>` becomes empty, removes `<back>` as well
- Does NOT remove `<back>` if it contains other material

### 6. Safety

- Does NOT change anything else in the document
- Does NOT reorder elements
- Does NOT alter unrelated attributes
- Preserves XML formatting and encoding
- Resulting document remains valid TEI P5 XML

## Edge Cases Handled

- `<ref>` occurring inside `<p>`, `<l>`, `<seg>`, `<q>`, etc.
- Endnotes containing multiple paragraphs or mixed inline elements
- Whitespace-only text nodes around `<ref>` elements
- Notes referenced out of order
- Notes that are never referenced (still removed with the notes div)
- Files without any endnotes (copied unchanged)
- `<back>` elements with mixed content (only notes div removed)

## Testing

The project includes a comprehensive test suite to validate transformations.

### Running Tests

```bash
python tests/test_transformations.py
```

### Test Cases

1. **Basic Inlining**: Simple endnotes with multiple references
2. **Complex Cases**: Nested markup, multiple elements, out-of-order references
3. **No Notes**: Files without endnotes remain unchanged
4. **Mixed References**: Files with both endnote refs and external refs

All tests validate:
- Correct number of inline notes created
- Proper removal of notes div and back element
- Preservation of nested markup
- No alteration of external references

## Project Structure

```
.
├── inline_notes.py              # Main transformation script
├── requirements.txt             # Python dependencies
├── setup_and_run.bat           # Windows batch file for easy setup
├── README.md                    # This file
├── Input/                       # Input TEI XML files (101 files)
├── Output/                      # Generated output files (gitignored)
└── tests/
    ├── test_transformations.py  # Test suite
    ├── test_input/              # Test input files
    └── test_output/             # Test output files
```

## Script Details

### Key Functions

- `get_notes_from_back()`: Extract endnotes from `<back><div type="notes">`
- `create_inline_note()`: Create inline note element from endnote
- `inline_references()`: Replace all `<ref>` elements with inline notes
- `remove_notes_div()`: Clean up `<back>` after inlining
- `process_file()`: Main processing function for a single file

### XML Processing

- Uses `lxml` library for robust TEI XML handling
- Respects TEI namespace (`http://www.tei-c.org/ns/1.0`)
- Preserves XML structure, formatting, and encoding
- Uses `deepcopy` for proper element duplication (multiple references)

## Example Transformation

### Before (Input)

```xml
<text>
  <body>
    <p>This is text with a reference<ref target="#N1"/>.</p>
  </body>
  <back>
    <div type="notes">
      <note xml:id="N1">This is the note content.</note>
    </div>
  </back>
</text>
```

### After (Output)

```xml
<text>
  <body>
    <p>This is text with a reference<note place="inline">This is the note content.</note>.</p>
  </body>
</text>
```

## Limitations

- Only processes XML files (`.xml` extension)
- Assumes TEI P5 XML with standard namespace
- Does not validate XML against TEI schema (preserves existing structure)
- Does not handle non-TEI XML formats

## License

This script was created for the ELTeC notes fix project to facilitate TEI Publisher rendering.

## Author

Generated for the ELTeC notes fix project.

## Support

For issues or questions, please refer to the test suite for examples of expected behavior.
