#!/usr/bin/env python3
"""
Extract unique gene transcripts from sorted JSON files.
"""

import json
import os
from pathlib import Path
from typing import Set

def extract_genes_from_input(input_text: str) -> Set[str]:
    """
    Extract gene names from the input text.
    Ignores numbers (one, two, three) and keywords (Genes, Gender, Class, Tissue).
    """
    # Number words to ignore
    number_words = {
        'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
    }
    
    # Gender values
    gender_values = {'male', 'female'}
    
    # Organ names (can appear as values after Tissue:)
    organ_names = {
        'Bladder', 'Brain', 'Kidney', 'Liver', 'Lung', 'Heart', 'Spleen',
        'Marrow', 'Muscle', 'bone-marrow', 'limb-muscle',
    }
    
    # Common cell type descriptors
    cell_descriptors = {
        'cell', 'urothelial', 'epithelial', 'endothelial', 'fibroblast', 'stromal',
        'mesenchymal', 'immune', 'lymphoid', 'myeloid', 'neuronal',
        'satellite', 'stem', 'thick', 'ascending', 'descending', 'tubule', 
        'proximal', 'distal', 'tissue', 'loop', 'limb', 'segment',
    }
    
    # Section keywords that indicate the start of a new field
    section_keywords = {'Genes:', 'Gender:', 'Class:', 'Tissue:'}
    
    # Combine all ignore sets
    ignore_words = number_words | gender_values | organ_names | cell_descriptors
    
    # Split the input text into tokens
    tokens = input_text.split()
    
    genes = set()
    skip_next = False
    
    for i, token in enumerate(tokens):
        # If we marked to skip this token (it was after a section keyword)
        if skip_next:
            skip_next = False
            continue
        
        # Skip section keywords and mark to skip the next token (which is the value)
        if token in section_keywords or token.endswith(':'):
            # For Gender:, Class:, and Tissue:, skip the next token (the value)
            if token in {'Gender:', 'Class:', 'Tissue:'}:
                skip_next = True
            continue
        
        # Skip ignore words (numbers, gender, organs, cell descriptors, etc.)
        if token in ignore_words or token.lower() in ignore_words:
            continue
        
        # Skip empty tokens
        if not token:
            continue
        
        # Add to genes set (valid gene names)
        genes.add(token)
    
    return genes

def main():
    # Set the data directory
    data_dir = Path(__file__).parent / 'data'
    
    # Find all JSON files ending with _sorted.json
    sorted_files = list(data_dir.glob('*_sorted.json'))
    
    print(f"Found {len(sorted_files)} sorted JSON files")
    
    # Collect all unique genes
    all_genes = set()
    
    # Process each file
    for file_path in sorted_files:
        print(f"Processing {file_path.name}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both list and single object formats
            if isinstance(data, list):
                entries = data
            else:
                entries = [data]
            
            # Extract genes from each entry
            for entry in entries:
                if 'input' in entry:
                    genes = extract_genes_from_input(entry['input'])
                    all_genes.update(genes)
        
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
    
    # Sort genes alphabetically for better readability
    sorted_genes = sorted(all_genes)
    
    print(f"\nFound {len(sorted_genes)} unique gene transcripts")
    
    # Write to gene_tokens.json
    output_file = data_dir / 'gene_tokens.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sorted_genes, f, indent=2, ensure_ascii=False)
    
    print(f"Gene tokens saved to {output_file}")
    
    # Print first 20 genes as sample
    print(f"\nSample genes (first 20):")
    for gene in sorted_genes[:20]:
        print(f"  - {gene}")

if __name__ == '__main__':
    main()
