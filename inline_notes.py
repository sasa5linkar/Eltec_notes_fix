#!/usr/bin/env python3
"""
TEI P5 Endnote Inlining Transformation Script

This script performs endnote inlining transformation on TEI P5 XML documents,
converting ELTeC-style endnotes (stored in <back><div type="notes">) into
inline notes suitable for TEI Publisher rendering.

Usage:
    python inline_notes.py <input_folder> <output_folder>

Author: Generated for ELTeC notes fix project
"""

import sys
import os
from pathlib import Path
from lxml import etree
from copy import deepcopy
from typing import Dict, List, Optional


# TEI namespace
TEI_NS = "http://www.tei-c.org/ns/1.0"
NSMAP = {None: TEI_NS}


def get_notes_from_back(root: etree._Element) -> Dict[str, etree._Element]:
    """
    Extract all endnotes from <back><div type="notes">.
    
    Args:
        root: The root element of the TEI document
        
    Returns:
        Dictionary mapping note xml:id to note element
    """
    notes = {}
    
    # Find all div elements with type="notes" inside back
    back_notes_divs = root.xpath(
        '//tei:back/tei:div[@type="notes"]',
        namespaces={'tei': TEI_NS}
    )
    
    # Extract all notes from these divs
    for div in back_notes_divs:
        note_elements = div.xpath('.//tei:note[@xml:id]', namespaces={'tei': TEI_NS})
        for note in note_elements:
            note_id = note.get('{http://www.w3.org/XML/1998/namespace}id')
            if note_id:
                notes[note_id] = note
    
    return notes


def create_inline_note(note_element: etree._Element) -> etree._Element:
    """
    Create an inline note element from an endnote.
    
    Args:
        note_element: The original note element from back/div[@type="notes"]
        
    Returns:
        New inline note element with place="inline" attribute
    """
    # Create new note element with place="inline"
    inline_note = etree.Element(f'{{{TEI_NS}}}note', nsmap=NSMAP)
    inline_note.set('place', 'inline')
    
    # Copy text content
    if note_element.text:
        inline_note.text = note_element.text
    
    # Copy all child elements (preserving mixed content)
    # Use deepcopy to ensure we don't move elements, allowing multiple references
    for child in note_element:
        inline_note.append(deepcopy(child))
    
    # Copy tail if present (text after last child element)
    if len(note_element) > 0 and note_element[-1].tail:
        inline_note[-1].tail = note_element[-1].tail
    
    return inline_note


def inline_references(root: etree._Element, notes: Dict[str, etree._Element]) -> int:
    """
    Replace all <ref> elements pointing to endnotes with inline notes.
    
    Args:
        root: The root element of the TEI document
        notes: Dictionary of note xml:id to note element
        
    Returns:
        Number of references inlined
    """
    count = 0
    
    # Find all ref elements with target attribute starting with #
    # Exclude refs in teiHeader
    refs = root.xpath(
        '//tei:text//tei:ref[starts-with(@target, "#")]',
        namespaces={'tei': TEI_NS}
    )
    
    for ref in refs:
        target = ref.get('target')
        if not target:
            continue
            
        # Extract note ID (remove # prefix)
        note_id = target[1:]
        
        # Check if this ref points to an endnote
        if note_id not in notes:
            continue
        
        # Create inline note from the endnote
        inline_note = create_inline_note(notes[note_id])
        
        # Preserve the tail of the ref (text after the ref element)
        if ref.tail:
            inline_note.tail = ref.tail
        
        # Replace ref with inline note
        parent = ref.getparent()
        if parent is not None:
            parent.replace(ref, inline_note)
            count += 1
    
    return count


def remove_notes_div(root: etree._Element) -> bool:
    """
    Remove the <div type="notes"> from <back>.
    If <back> becomes empty, remove it as well.
    
    Args:
        root: The root element of the TEI document
        
    Returns:
        True if div was removed, False otherwise
    """
    # Find and remove all div[@type="notes"] in back
    notes_divs = root.xpath(
        '//tei:back/tei:div[@type="notes"]',
        namespaces={'tei': TEI_NS}
    )
    
    if not notes_divs:
        return False
    
    for notes_div in notes_divs:
        back = notes_div.getparent()
        back.remove(notes_div)
        
        # Check if back is now empty (only whitespace text and no child elements)
        if back is not None:
            # Check for any non-whitespace content or child elements
            has_content = False
            
            # Check for child elements
            if len(back) > 0:
                has_content = True
            
            # Check for non-whitespace text
            if not has_content and back.text and back.text.strip():
                has_content = True
            
            # If back is empty, remove it
            if not has_content:
                text_element = back.getparent()
                if text_element is not None:
                    text_element.remove(back)
    
    return True


def process_file(input_path: Path, output_path: Path) -> bool:
    """
    Process a single TEI XML file: inline endnotes and save result.
    
    Args:
        input_path: Path to input XML file
        output_path: Path to output XML file
        
    Returns:
        True if processing succeeded, False otherwise
    """
    try:
        # Parse XML file
        parser = etree.XMLParser(remove_blank_text=False, encoding='utf-8')
        tree = etree.parse(str(input_path), parser)
        root = tree.getroot()
        
        # Extract endnotes from back
        notes = get_notes_from_back(root)
        
        if not notes:
            # No endnotes found, just copy the file
            tree.write(
                str(output_path),
                encoding='utf-8',
                xml_declaration=True,
                pretty_print=False
            )
            print(f"  No endnotes found in {input_path.name}")
            return True
        
        print(f"  Found {len(notes)} endnotes in {input_path.name}")
        
        # Inline all references to endnotes
        inlined_count = inline_references(root, notes)
        print(f"  Inlined {inlined_count} references")
        
        # Remove notes div from back
        remove_notes_div(root)
        
        # Write output file
        tree.write(
            str(output_path),
            encoding='utf-8',
            xml_declaration=True,
            pretty_print=False
        )
        
        print(f"  Successfully processed {input_path.name}")
        return True
        
    except Exception as e:
        print(f"  ERROR processing {input_path.name}: {e}")
        return False


def main():
    """Main entry point for the script."""
    if len(sys.argv) != 3:
        print("Usage: python inline_notes.py <input_folder> <output_folder>")
        sys.exit(1)
    
    input_folder = Path(sys.argv[1])
    output_folder = Path(sys.argv[2])
    
    # Validate input folder
    if not input_folder.exists() or not input_folder.is_dir():
        print(f"Error: Input folder '{input_folder}' does not exist or is not a directory")
        sys.exit(1)
    
    # Create output folder if it doesn't exist
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Find all XML files in input folder
    xml_files = list(input_folder.glob("*.xml"))
    
    if not xml_files:
        print(f"No XML files found in {input_folder}")
        sys.exit(1)
    
    print(f"Found {len(xml_files)} XML files to process")
    print(f"Input folder: {input_folder}")
    print(f"Output folder: {output_folder}")
    print()
    
    # Process each file
    success_count = 0
    error_count = 0
    
    for xml_file in xml_files:
        output_path = output_folder / xml_file.name
        print(f"Processing {xml_file.name}...")
        
        if process_file(xml_file, output_path):
            success_count += 1
        else:
            error_count += 1
        print()
    
    # Print summary
    print("=" * 70)
    print(f"Processing complete!")
    print(f"Successfully processed: {success_count} files")
    print(f"Errors: {error_count} files")
    print(f"Output saved to: {output_folder}")


if __name__ == "__main__":
    main()
