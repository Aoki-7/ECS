#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3 测试

覆盖：
- 认知框架
- 记忆扭曲引擎
- 传话游戏效应
"""

import sys
sys.path.insert(0, r"D:\个人助手\workspace\ECS")

import unittest

from memory_layer import SensoryDescription, EmotionalTag
from memory_layer.cognitive_framework import (
    CognitiveFramework,
    create_animal_framework,
    create_human_framework,
)
from memory_layer.memory_distortion import MemoryDistortionEngine, simulate_telephone_game


class TestCognitiveFramework(unittest.TestCase):
    """测试认知框架"""

    def test_attention_filter(self):
        """测试注意力滤镜"""
        framework = CognitiveFramework()
        framework.attention_weights["shape"] = 2.0  # 高权重，不易丢失
        framework.attention_weights["color"] = 0.1  # 低权重，容易丢失

        desc = SensoryDescription(shape="圆形", color="灰色", texture="光滑")
        filtered = framework.apply_attention_filter(desc, base_attention=0.5)

        # 形状权重高，应该保留
        self.assertIsNotNone(filtered.shape)
        # 颜色权重低，可能丢失（概率性，多次测试）
        # 这里不断言具体结果，只验证方法不报错

    def test_interpretation_bias(self):
        """测试解释偏差"""
        framework = CognitiveFramework()
        framework.interpretation_bias = {
            "color": {"灰色": ["暗色", "灰白色"]},
        }

        desc = SensoryDescription(shape="圆形", color="灰色")
        biased = framework.apply_interpretation_bias(desc)

        # 灰色应被解释为暗色或灰白色
        self.assertIn(biased.color, ["暗色", "灰白色"])
        # 形状不应被影响
        self.assertEqual(biased.shape, "圆形")

    def test_threat_filter(self):
        """测试威胁滤镜"""
        framework = CognitiveFramework()
        framework.threat_sensitivity = 0.9  # 高敏感度

        desc = SensoryDescription(size="中等", sound="低沉")
        filtered = framework.apply_threat_filter(desc, is_threat=True)

        # 大小应被夸大
        self.assertEqual(filtered.size, "大")
        # 声音应变得更可怕
        self.assertEqual(filtered.sound, "威胁性低吼")

    def test_reconstruct_memory(self):
        """测试记忆重构"""
        framework = CognitiveFramework()

        # 部分缺失的描述
        partial = SensoryDescription(shape="圆形")  # 只有形状
        reconstructed = framework.reconstruct_memory(partial)

        # 应基于关联填补缺失字段
        # 圆形 → 灰色, 光滑
        self.assertIsNotNone(reconstructed.color)
        self.assertIsNotNone(reconstructed.texture)

    def test_animal_framework(self):
        """测试动物认知框架"""
        predator = create_animal_framework("predator")
        self.assertGreater(predator.attention_weights["size"], 1.0)
        self.assertLess(predator.threat_sensitivity, 0.5)

        prey = create_animal_framework("prey")
        self.assertGreater(prey.attention_weights["size"], 1.0)
        self.assertGreater(prey.threat_sensitivity, 0.8)

    def test_human_framework(self):
        """测试人类认知框架"""
        human = create_human_framework()
        self.assertGreater(human.attention_weights["color"], 1.0)
        self.assertIn("color", human.interpretation_bias)


class TestMemoryDistortion(unittest.TestCase):
    """测试记忆扭曲引擎"""

    def setUp(self):
        self.engine = MemoryDistortionEngine(seed=42)

    def test_information_loss(self):
        """测试信息损失"""
        desc = SensoryDescription(shape="圆形", color="灰色", texture="光滑")
        emotion = EmotionalTag(primary="fear", intensity=0.8)

        distorted_desc, distorted_emotion, confidence = self.engine.distort(
            desc, emotion, narrator_confidence=0.9
        )

        # 高确信度，大部分信息应保留
        self.assertIsNotNone(distorted_desc.shape)
        self.assertLess(confidence, 0.9)  # 确信度应降低

    def test_low_confidence_loss(self):
        """测试低确信度导致大量信息丢失"""
        desc = SensoryDescription(shape="圆形", color="灰色", texture="光滑")
        emotion = EmotionalTag(primary="fear", intensity=0.8)

        distorted_desc, _, confidence = self.engine.distort(
            desc, emotion, narrator_confidence=0.2
        )

        # 低确信度，很多信息可能丢失
        self.assertLess(confidence, 0.2)
        # 至少有一些字段丢失
        lost_count = sum(
            1 for f in ["shape", "color", "texture"]
            if getattr(distorted_desc, f) is None
        )
        self.assertGreater(lost_count, 0)

    def test_emotion_contagion(self):
        """测试情感传染"""
        desc = SensoryDescription(shape="圆形")
        emotion = EmotionalTag(primary="fear", intensity=0.9)

        _, distorted_emotion, _ = self.engine.distort(
            desc, emotion, narrator_confidence=0.8
        )

        # 情感强度应减弱
        self.assertLess(distorted_emotion.intensity, emotion.intensity)

    def test_distortion_level_calculation(self):
        """测试扭曲度计算"""
        orig = SensoryDescription(shape="圆形", color="灰色", texture="光滑")
        dist = SensoryDescription(shape="圆形", color="暗色", texture=None)

        level = self.engine.calculate_distortion_level(orig, dist)
        # 颜色变了(1) + texture丢失(1) = 2/3 不匹配
        self.assertAlmostEqual(level, 2/3, places=1)

    def test_telephone_game(self):
        """测试传话游戏效应"""
        desc = SensoryDescription(shape="圆形", color="灰色", texture="光滑")
        emotion = EmotionalTag(primary="fear", intensity=0.8)

        chain = simulate_telephone_game(
            self.engine,
            desc,
            emotion,
            chain_length=5,
            initial_confidence=0.95,
        )

        # 链长度应为 6（原始 + 5次传递）
        self.assertEqual(len(chain), 6)

        # 确信度应递减
        for i in range(1, len(chain)):
            self.assertLessEqual(chain[i][2], chain[i-1][2])

        # 最终扭曲度应很高
        final_desc = chain[-1][0]
        distortion = self.engine.calculate_distortion_level(desc, final_desc)
        self.assertGreater(distortion, 0.3)

    def test_cognitive_framework_distortion(self):
        """测试认知框架导致的扭曲"""
        desc = SensoryDescription(shape="圆形", color="灰色", texture="光滑", size="中等")
        emotion = EmotionalTag(primary="fear", intensity=0.6)

        # 使用猎物框架（高威胁敏感度）
        prey_framework = create_animal_framework("prey")

        distorted_desc, distorted_emotion, confidence = self.engine.distort(
            desc,
            emotion,
            narrator_confidence=0.8,
            receiver_framework=prey_framework,
            is_threat_context=True,
        )

        # 猎物框架在威胁上下文中会夸大大小
        if distorted_desc.size:
            self.assertNotEqual(distorted_desc.size, "中等")

        # 情感强度可能因威胁滤镜而增强
        self.assertGreaterEqual(distorted_emotion.intensity, emotion.intensity * 0.5)


class TestIntegrationPhase3(unittest.TestCase):
    """Phase 3 集成测试"""

    def test_full_distortion_chain(self):
        """测试完整扭曲链"""
        engine = MemoryDistortionEngine(seed=123)

        # 原始记忆：捕食者看到的猎物
        original = SensoryDescription(
            shape="四足",
            color="棕色",
            texture="毛茸茸",
            size="中等",
            sound="沙沙响",
        )
        emotion = EmotionalTag(primary="curiosity", intensity=0.7)

        # 捕食者框架
        predator = create_animal_framework("predator")

        # 猎物框架
        prey = create_animal_framework("prey")

        # 捕食者观察猎物
        predator_memory, pred_emotion, pred_conf = engine.distort(
            original, emotion, 0.95, predator, is_threat_context=False
        )

        # 猎物观察捕食者（威胁上下文）
        prey_memory, prey_emotion, prey_conf = engine.distort(
            original, emotion, 0.95, prey, is_threat_context=True
        )

        # 猎物的记忆应更恐惧（或至少不低于捕食者）
        self.assertGreaterEqual(prey_emotion.intensity, pred_emotion.intensity * 0.9)

        # 猎物的记忆应有威胁滤镜导致的扭曲
        distortion = engine.calculate_distortion_level(original, prey_memory)
        self.assertGreater(distortion, 0.1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
