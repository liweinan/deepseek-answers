#!/usr/bin/env python3
import re
import sys

def detect_language(text):
    """Detect if text contains Chinese characters or is primarily English"""
    # Chinese character ranges
    chinese_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf]')
    
    # Count Chinese characters
    chinese_chars = len(chinese_pattern.findall(text))
    
    # Count English words (simple heuristic)
    english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
    
    # Count total characters
    total_chars = len(text)
    
    print(f"File analysis:")
    print(f"  Chinese characters: {chinese_chars}")
    print(f"  English words: {english_words}")
    print(f"  Total characters: {total_chars}")
    
    if chinese_chars > 0:
        return True, f"Contains {chinese_chars} Chinese characters"
    else:
        return False, "No Chinese characters detected"

def check_file(filepath):
    """Check if a file contains Chinese characters"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            has_chinese, message = detect_language(content)
            return has_chinese, message, content[:200]  # First 200 chars for preview
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False, str(e), ""

def main():
    files_to_check = [
        "files/hr-a-very-big-sum.md",
        "files/hr-blogpost.md", 
        "files/hr-compare-the-triplets.md",
        "files/hr-contactform.md",
        "files/hr-cryptorank-exchange.md",
        "files/hr-itemlistmanager.md",
        "files/hr-patient.md",
        "files/hr-sherlock.md"
    ]
    
    print("=== Language Detection Results ===\n")
    
    for filepath in files_to_check:
        print(f"File: {filepath}")
        has_chinese, message, preview = check_file(filepath)
        print(f"  Result: {message}")
        print(f"  Preview: {preview[:100]}...")
        print()
    
    return

if __name__ == "__main__":
    main()