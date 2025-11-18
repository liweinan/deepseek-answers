#!/usr/bin/env python3
import re
import sys

def contains_chinese(text):
    """Check if text contains Chinese characters"""
    # Unicode ranges for Chinese characters
    chinese_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\u20000-\u2a6df\u2a700-\u2b73f\u2b740-\u2b81f\u2b820-\u2ceaf\uf900-\ufaff\u3000-\u303f]')
    return bool(chinese_pattern.search(text))

def check_file(filepath):
    """Check if a file contains Chinese characters"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            has_chinese = contains_chinese(content)
            return has_chinese, content
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False, ""

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
    
    results = {}
    for filepath in files_to_check:
        has_chinese, content = check_file(filepath)
        results[filepath] = {
            'has_chinese': has_chinese,
            'content': content[:500] if len(content) > 500 else content  # First 500 chars for preview
        }
        print(f"{filepath}: {'Chinese found' if has_chinese else 'No Chinese'}")
    
    return results

if __name__ == "__main__":
    results = main()