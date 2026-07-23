#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
物种形成分析器

职责：
    - 基因向量聚类分析
    - 计算中心点和欧氏距离
    - 识别离群子群
"""

import math
from typing import List, Tuple


class SpeciationAnalyzer:
    """物种形成分析器"""

    def __init__(self, threshold: float = 2.0, min_group_size: int = 5):
        self.threshold = threshold
        self.min_group_size = min_group_size

    def find_outlier_cluster(
        self, id_vectors: List[Tuple[int, List[float]]]
    ) -> List[Tuple[int, List[float]]]:
        """
        在群体中寻找离群子群（使用 k-means 启发式）— 优化版：缓存距离计算

        Returns:
            离群子群的 (entity_id, vector) 列表，无则返回空列表
        """
        vectors = [v for _, v in id_vectors]
        centroid = self.compute_centroid(vectors)

        if len(vectors) < self.min_group_size * 2:
            return []

        # 找距离中心最远的个体作为种子 A
        seed_a = max(id_vectors, key=lambda x: self.euclidean_distance(x[1], centroid))

        # 找距离种子 A 最远的个体作为种子 B
        seed_b = max(id_vectors, key=lambda x: self.euclidean_distance(x[1], seed_a[1]))

        # 分配个体到两个聚类 — 缓存距离避免重复计算
        cluster_a = []
        cluster_b = []

        # 预计算种子 A 和 B 的距离
        dist_a_cache = {item[0]: self.euclidean_distance(item[1], seed_a[1]) for item in id_vectors}
        dist_b_cache = {item[0]: self.euclidean_distance(item[1], seed_b[1]) for item in id_vectors}

        for item in id_vectors:
            eid, vector = item
            dist_a = dist_a_cache[eid]
            dist_b = dist_b_cache[eid]
            if dist_a <= dist_b:
                cluster_a.append(item)
            else:
                cluster_b.append(item)

        # 确保 cluster_b 是较小的那个
        if len(cluster_a) < len(cluster_b):
            cluster_a, cluster_b = cluster_b, cluster_a

        # 小聚类必须满足最小群体大小
        if len(cluster_b) < self.min_group_size:
            return []

        # 计算两聚类中心距离
        centroid_a = self.compute_centroid([v for _, v in cluster_a])
        centroid_b = self.compute_centroid([v for _, v in cluster_b])
        inter_distance = self.euclidean_distance(centroid_a, centroid_b)

        if inter_distance < self.threshold:
            return []

        return cluster_b

    def compute_centroid(self, vectors: List[List[float]]) -> List[float]:
        """计算一组向量的中心点（各维度平均值）"""
        if not vectors:
            return []
        dim = len(vectors[0])
        centroid = []
        for i in range(dim):
            values = [v[i] for v in vectors]
            centroid.append(sum(values) / len(values))
        return centroid

    def euclidean_distance(self, a: List[float], b: List[float]) -> float:
        """计算两个向量的欧氏距离"""
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))