#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找模拟最终统计信息
"""
import sys
import os

def find_final_stats(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if '模拟结束' in line or '最终统计' in line:
                print(f'找到最终统计信息，从第{i+1}行开始：')
                for j in range(i, min(i+50, len(lines))):
                    print(lines[j].strip())
                return
    print('未找到最终统计信息')

if __name__ == "__main__":
    find_final_stats('long_simulation_output.txt')