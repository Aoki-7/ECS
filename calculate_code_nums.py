#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:test1.py
@说明:计算代码行数
@时间:2026/03/24 15:36:39
@作者:Sherry
@版本:1.0
'''



import os


def count_lines_in_file(file_path):
   total, code, comments, empty = 0, 0, 0, 0
   with open(file_path, 'r', encoding='utf-8') as f:
       for line in f:
           total += 1
           stripped = line.strip()
           if not stripped:
               empty += 1
           elif stripped.startswith('#'):
               comments += 1
           else:
               code += 1
   return total, code, comments, empty


def count_lines_in_directory(directory):
   total = code = comments = empty = 0
   for root, _, files in os.walk(directory):
       for file in files:
           if file.endswith('.py'):
               t, c, cm, e = count_lines_in_file(os.path.join(root, file))
               total += t; code += c; comments += cm; empty += e
   return total, code, comments, empty


if __name__ == "__main__":
   path = "../ECS"
   t, c, cm, e = count_lines_in_directory(path)
   print(f"总行数: {t}, 代码行: {c}, 注释行: {cm}, 空行: {e}")