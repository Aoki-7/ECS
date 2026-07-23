#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:life_stage_evaluator.py
@说明:人生阶段评估器

职责：
    - 根据年龄确定人生阶段
'''

from typing import Tuple


class LifeStageEvaluator:
    """人生阶段评估器"""

    def __init__(self, childhood: Tuple[int, int], adolescence: Tuple[int, int],
                 adulthood: Tuple[int, int], elderhood: Tuple[int, int]):
        self.childhood = childhood
        self.adolescence = adolescence
        self.adulthood = adulthood
        self.elderhood = elderhood

    def get_life_stage(self, age: float) -> str:
        """
        根据年龄确定人生阶段

        Args:
            age: 年龄（岁）

        Returns:
            str: 人生阶段标识
        """
        # 防御：如果 age 是对象，尝试获取 current_age / age / value 属性
        if hasattr(age, 'current_age'):
            age = age.current_age
        elif hasattr(age, 'age'):
            age = age.age
        elif hasattr(age, 'value'):
            age = age.value
        elif not isinstance(age, (int, float)):
            age = 25.0  # 默认成年

        if age < self.childhood[1]:
            return "childhood"
        elif age < self.adolescence[1]:
            return "adolescence"
        elif age < self.adulthood[1]:
            return "adulthood"
        else:
            return "elderhood"