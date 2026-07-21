#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找社会结构详情
"""
import sys

def find_social_structure(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        in_social_section = False
        for line in lines:
            if '最终社会结构详情:' in line:
                in_social_section = True
                print(line.strip())
                continue
            if in_social_section:
                print(line.strip())
                if '====' in line and len(line.strip()) > 60:
                    break

if __name__ == "__main__":
    find_social_structure('long_simulation_output.txt')
