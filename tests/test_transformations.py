#!/usr/bin/env python3
"""
Test script for endnote inlining transformations.

This script tests the inline_notes.py transformation on test files
and validates the results.
"""

import sys
from pathlib import Path
from lxml import etree

# Add parent directory to path to import inline_notes
sys.path.insert(0, str(Path(__file__).parent.parent))

import inline_notes

TEI_NS = "http://www.tei-c.org/ns/1.0"


def count_elements(root, xpath):
    """Count elements matching an XPath expression."""
    return len(root.xpath(xpath, namespaces={'tei': TEI_NS}))


def test_basic_inlining():
    """Test basic endnote inlining functionality."""
    print("Test 1: Basic Endnote Inlining")
    print("-" * 50)
    
    input_file = Path("tests/test_input/test_basic.xml")
    output_file = Path("tests/test_output/test_basic.xml")
    
    # Process the file
    success = inline_notes.process_file(input_file, output_file)
    
    if not success:
        print("  FAILED: Processing failed")
        return False
    
    # Parse output and check results
    tree = etree.parse(str(output_file))
    root = tree.getroot()
    
    # Check that inline notes were created
    inline_notes_count = count_elements(root, '//tei:text//tei:note[@place="inline"]')
    
    # Check that back/div[@type="notes"] was removed
    notes_div_count = count_elements(root, '//tei:back/tei:div[@type="notes"]')
    
    # Check that back element was removed (since it only had notes)
    back_count = count_elements(root, '//tei:back')
    
    # Check that original refs were removed
    ref_to_notes = count_elements(root, '//tei:text//tei:ref[starts-with(@target, "#TEST001_N")]')
    
    print(f"  Inline notes created: {inline_notes_count} (expected: 4)")
    print(f"  Notes div remaining: {notes_div_count} (expected: 0)")
    print(f"  Back element remaining: {back_count} (expected: 0)")
    print(f"  Refs to notes remaining: {ref_to_notes} (expected: 0)")
    
    passed = (
        inline_notes_count == 4 and
        notes_div_count == 0 and
        back_count == 0 and
        ref_to_notes == 0
    )
    
    print(f"  Result: {'PASSED' if passed else 'FAILED'}")
    print()
    return passed


def test_complex_cases():
    """Test complex cases including nested markup and multiple references."""
    print("Test 2: Complex Cases")
    print("-" * 50)
    
    input_file = Path("tests/test_input/test_complex.xml")
    output_file = Path("tests/test_output/test_complex.xml")
    
    # Process the file
    success = inline_notes.process_file(input_file, output_file)
    
    if not success:
        print("  FAILED: Processing failed")
        return False
    
    # Parse output and check results
    tree = etree.parse(str(output_file))
    root = tree.getroot()
    
    # Check that inline notes were created (5 refs total)
    inline_notes_count = count_elements(root, '//tei:text//tei:note[@place="inline"]')
    
    # Check that nested markup was preserved
    inline_with_hi = count_elements(root, '//tei:text//tei:note[@place="inline"]//tei:hi')
    inline_with_foreign = count_elements(root, '//tei:text//tei:note[@place="inline"]//tei:foreign')
    
    # Check that notes div was removed
    notes_div_count = count_elements(root, '//tei:back/tei:div[@type="notes"]')
    
    print(f"  Inline notes created: {inline_notes_count} (expected: 5)")
    print(f"  Inline notes with <hi>: {inline_with_hi} (expected: ≥2)")
    print(f"  Inline notes with <foreign>: {inline_with_foreign} (expected: ≥1)")
    print(f"  Notes div remaining: {notes_div_count} (expected: 0)")
    
    passed = (
        inline_notes_count == 5 and
        inline_with_hi >= 2 and
        inline_with_foreign >= 1 and
        notes_div_count == 0
    )
    
    print(f"  Result: {'PASSED' if passed else 'FAILED'}")
    print()
    return passed


def test_no_notes():
    """Test file without endnotes - should be unchanged."""
    print("Test 3: File Without Endnotes")
    print("-" * 50)
    
    input_file = Path("tests/test_input/test_no_notes.xml")
    output_file = Path("tests/test_output/test_no_notes.xml")
    
    # Process the file
    success = inline_notes.process_file(input_file, output_file)
    
    if not success:
        print("  FAILED: Processing failed")
        return False
    
    # Parse output and check results
    tree = etree.parse(str(output_file))
    root = tree.getroot()
    
    # Check that no inline notes were created
    inline_notes_count = count_elements(root, '//tei:text//tei:note[@place="inline"]')
    
    # Check that back element still exists (it has other content)
    back_count = count_elements(root, '//tei:back')
    
    # Check that liminal div is still there
    liminal_div_count = count_elements(root, '//tei:back/tei:div[@type="liminal"]')
    
    print(f"  Inline notes created: {inline_notes_count} (expected: 0)")
    print(f"  Back element remaining: {back_count} (expected: 1)")
    print(f"  Liminal div remaining: {liminal_div_count} (expected: 1)")
    
    passed = (
        inline_notes_count == 0 and
        back_count == 1 and
        liminal_div_count == 1
    )
    
    print(f"  Result: {'PASSED' if passed else 'FAILED'}")
    print()
    return passed


def test_mixed_references():
    """Test file with mixed reference types."""
    print("Test 4: Mixed Reference Types")
    print("-" * 50)
    
    input_file = Path("tests/test_input/test_mixed_refs.xml")
    output_file = Path("tests/test_output/test_mixed_refs.xml")
    
    # Process the file
    success = inline_notes.process_file(input_file, output_file)
    
    if not success:
        print("  FAILED: Processing failed")
        return False
    
    # Parse output and check results
    tree = etree.parse(str(output_file))
    root = tree.getroot()
    
    # Check that inline notes were created from endnote refs
    inline_notes_count = count_elements(root, '//tei:text//tei:note[@place="inline"]')
    
    # Check that external refs are still present
    external_refs = count_elements(root, '//tei:text//tei:ref[@target="http://example.com"]')
    
    # Check that notes div was removed
    notes_div_count = count_elements(root, '//tei:back/tei:div[@type="notes"]')
    
    # Check that other back content remains
    back_count = count_elements(root, '//tei:back')
    liminal_div_count = count_elements(root, '//tei:back/tei:div[@type="liminal"]')
    
    print(f"  Inline notes created: {inline_notes_count} (expected: 3)")
    print(f"  External refs remaining: {external_refs} (expected: 1)")
    print(f"  Notes div remaining: {notes_div_count} (expected: 0)")
    print(f"  Back element remaining: {back_count} (expected: 1)")
    print(f"  Liminal div remaining: {liminal_div_count} (expected: 1)")
    
    passed = (
        inline_notes_count == 3 and
        external_refs == 1 and
        notes_div_count == 0 and
        back_count == 1 and
        liminal_div_count == 1
    )
    
    print(f"  Result: {'PASSED' if passed else 'FAILED'}")
    print()
    return passed


def test_bom_handling():
    """Test file with UTF-8 BOM - should handle BOM correctly."""
    print("Test 5: UTF-8 BOM Handling")
    print("-" * 50)
    
    input_file = Path("tests/test_input/test_bom.xml")
    output_file = Path("tests/test_output/test_bom.xml")
    
    # Verify input file has BOM
    with open(input_file, 'rb') as f:
        input_content = f.read()
    
    has_input_bom = input_content.startswith(b'\xef\xbb\xbf')
    print(f"  Input file has BOM: {has_input_bom} (expected: True)")
    
    if not has_input_bom:
        print("  FAILED: Test file should have BOM")
        return False
    
    # Process the file
    success = inline_notes.process_file(input_file, output_file)
    
    if not success:
        print("  FAILED: Processing failed")
        return False
    
    # Verify output file does not have BOM
    with open(output_file, 'rb') as f:
        output_content = f.read()
    
    has_output_bom = output_content.startswith(b'\xef\xbb\xbf')
    print(f"  Output file has BOM: {has_output_bom} (expected: False)")
    
    # Verify output starts with XML declaration
    starts_with_xml = output_content.startswith(b'<?xml')
    print(f"  Output starts with XML declaration: {starts_with_xml} (expected: True)")
    
    # Parse output and check results
    tree = etree.parse(str(output_file))
    root = tree.getroot()
    
    # Check that inline notes were created
    inline_notes_count = count_elements(root, '//tei:text//tei:note[@place="inline"]')
    
    # Check that back/div[@type="notes"] was removed
    notes_div_count = count_elements(root, '//tei:back/tei:div[@type="notes"]')
    
    # Check that back element was removed (since it only had notes)
    back_count = count_elements(root, '//tei:back')
    
    print(f"  Inline notes created: {inline_notes_count} (expected: 2)")
    print(f"  Notes div remaining: {notes_div_count} (expected: 0)")
    print(f"  Back element remaining: {back_count} (expected: 0)")
    
    passed = (
        has_input_bom and
        not has_output_bom and
        starts_with_xml and
        inline_notes_count == 2 and
        notes_div_count == 0 and
        back_count == 0
    )
    
    print(f"  Result: {'PASSED' if passed else 'FAILED'}")
    print()
    return passed


def main():
    """Run all tests."""
    print("=" * 70)
    print("Endnote Inlining Transformation Tests")
    print("=" * 70)
    print()
    
    # Create output directory if needed
    Path("tests/test_output").mkdir(parents=True, exist_ok=True)
    
    # Run tests
    results = []
    results.append(("Basic Inlining", test_basic_inlining()))
    results.append(("Complex Cases", test_complex_cases()))
    results.append(("No Notes", test_no_notes()))
    results.append(("Mixed References", test_mixed_references()))
    results.append(("BOM Handling", test_bom_handling()))
    
    # Summary
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"  {name}: {status}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nAll tests passed! ✓")
        return 0
    else:
        print(f"\n{total - passed} test(s) failed! ✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
