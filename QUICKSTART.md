# Quick Start Guide

This guide will help you quickly get started with the TEI Endnote Inlining Transformation script.

## Prerequisites

- Python 3.7 or higher installed
- Input TEI XML files in the `Input` folder

## Quick Start (Windows)

1. Double-click `setup_and_run.bat`
2. The script will automatically:
   - Create a virtual environment
   - Install dependencies (lxml)
   - Process all files from `Input` to `Output`
3. Check the `Output` folder for transformed files

## Quick Start (Linux/Mac)

1. Open a terminal in the project directory
2. Run: `./setup_and_run.sh`
3. The script will automatically:
   - Create a virtual environment
   - Install dependencies (lxml)
   - Process all files from `Input` to `Output`
4. Check the `Output` folder for transformed files

## Manual Usage

If you prefer to run the script manually:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the transformation
python inline_notes.py Input Output
```

## What Gets Transformed?

The script will:
- Find all endnotes in `<back><div type="notes">`
- Replace each `<ref target="#NOTE_ID"/>` with `<note place="inline">NOTE_CONTENT</note>`
- Remove the notes div from the back matter
- Preserve all other content unchanged

## Example

**Before:**
```xml
<p>Text with reference<ref target="#N1"/>.</p>
...
<back>
  <div type="notes">
    <note xml:id="N1">Note content.</note>
  </div>
</back>
```

**After:**
```xml
<p>Text with reference<note place="inline">Note content.</note>.</p>
```

## Verification

To verify the transformation worked correctly:

1. Check the console output - it shows statistics for each file
2. Look at the final summary showing total files processed
3. Compare a file from `Input` with its counterpart in `Output`

## Testing

To run the test suite:

```bash
python tests/test_transformations.py
```

All 4 tests should pass.

## Need Help?

- See `README.md` for detailed documentation
- Check the test files in `tests/test_input/` for examples
- Review transformation rules in the README
