#!/usr/bin/env python3
import re
import sys
import os

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
        "files/konflux-ci.md",
        "files/kube-proxy-cni.md",
        "files/kube-proxy-intro.md",
        "files/kubelet-intro.md",
        "files/langchain4j-use.md",
        "files/lb-vs-clusterip.md",
        "files/leetcode-cheatsheet.md",
        "files/metallb-more.md",
        "files/metallb-vs-aws-elb.md",
        "files/mlflow-vs-kubeflow.md",
        "files/models-intro.md",
        "files/nested-hell.md",
        "files/new-year-chaos.md",
        "files/nextjs.md",
        "files/nextjs2.md"
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