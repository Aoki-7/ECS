#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:test_phase2_components.py
@说明:Phase 2组件测试
@时间:2026/07/19
@版本:1.0
'''

import pytest
from core.world import World
from human.components.social.social_component_v4 import SocialManagerComponent, RelationshipType, InteractionType, SocialRole, SocialStatus
from human.components.cognitive.cognitive_component_v4 import CognitiveComponent, LearningStyle, DecisionStyle, RiskPreference
from human.components.perception.perception_component_v4 import PerceptionComponent, VisionType, HearingType, SpatialAwareness
from human.components.basic.human_component import HumanComponent
from space.space_component import SpaceComponent
from human.components.cognitive.intent_component import IntentComponent, IntentType


class TestSocialComponent:
    """社会组件测试"""
    
    def test_social_initialization(self):
        """测试社会组件初始化"""
        social = SocialManagerComponent()
        
        # 检查关系系统
        assert len(social.relationships) == 0
        assert social.next_relationship_id == 0
        
        # 检查社会角色
        assert len(social.current_roles) == 0
        assert len(social.role_history) == 0
        
        # 检查社会地位
        assert len(social.social_status) == 0
        assert social.overall_status == 0.5
        
        # 检查社会互动
        assert len(social.active_interactions) == 0
        assert social.next_interaction_id == 0
        
        # 检查社会网络
        assert len(social.social_network) == 0
        assert social.network_centrality == 0.5
    
    def test_add_relationship(self):
        """测试添加关系"""
        social = SocialManagerComponent()
        
        # 添加关系
        relationship_id = social.add_relationship(1, RelationshipType.FRIEND, strength=0.7)
        
        # 检查关系
        assert relationship_id in social.relationships
        assert social.relationships[relationship_id].target_id == 1
        assert social.relationships[relationship_id].relationship_type == RelationshipType.FRIEND
        assert social.relationships[relationship_id].strength == 0.7
        
        # 检查实体关系映射
        assert 1 in social.relationship_by_entity
        assert relationship_id in social.relationship_by_entity[1]
    
    def test_get_relationship(self):
        """测试获取关系"""
        social = SocialManagerComponent()
        
        # 添加关系
        relationship_id = social.add_relationship(1, RelationshipType.FRIEND, strength=0.7)
        
        # 获取关系
        relationship = social.get_relationship(1)
        
        # 检查关系
        assert relationship is not None
        assert relationship.relationship_id == relationship_id
        assert relationship.target_id == 1
        assert relationship.relationship_type == RelationshipType.FRIEND
    
    def test_update_relationship(self):
        """测试更新关系"""
        social = SocialManagerComponent()
        
        # 添加关系
        social.add_relationship(1, RelationshipType.FRIEND, strength=0.5)
        
        # 更新关系
        social.update_relationship(1, InteractionType.HELP, outcome=0.8)
        
        # 检查关系强度
        relationship = social.get_relationship(1)
        assert relationship.strength > 0.5  # 正面互动增加关系强度
    
    def test_add_role(self):
        """测试添加角色"""
        social = SocialManagerComponent()
        
        # 添加角色
        role_info = social.add_role(SocialRole.TEACHER, responsibilities=["教学", "指导"])
        
        # 检查角色
        assert len(social.current_roles) == 1
        assert social.current_roles[0].role == SocialRole.TEACHER
        assert social.current_roles[0].responsibilities == ["教学", "指导"]
        
        # 检查是否有角色
        assert social.has_role(SocialRole.TEACHER)
        assert not social.has_role(SocialRole.STUDENT)
    
    def test_add_status(self):
        """测试添加社会地位"""
        social = SocialManagerComponent()
        
        # 添加社会地位
        status_info = social.add_status(SocialStatus.EXPERT, level=0.8)
        
        # 检查社会地位
        assert SocialStatus.EXPERT in social.social_status
        assert social.social_status[SocialStatus.EXPERT].level == 0.8
        
        # 检查整体地位
        assert social.overall_status > 0.5
    
    def test_add_interaction(self):
        """测试添加社会互动"""
        social = SocialManagerComponent()
        
        # 添加互动
        interaction_id = social.add_interaction(InteractionType.CONVERSATION, [1, 2])
        
        # 检查互动
        assert interaction_id in social.active_interactions
        assert social.active_interactions[interaction_id].interaction_type == InteractionType.CONVERSATION
        assert social.active_interactions[interaction_id].participants == [1, 2]
        
        # 检查社会网络
        assert 1 in social.social_network
        assert 2 in social.social_network
        assert 2 in social.social_network[1]
        assert 1 in social.social_network[2]
    
    def test_complete_interaction(self):
        """测试完成社会互动"""
        social = SocialManagerComponent()
        
        # 添加关系
        social.add_relationship(1, RelationshipType.FRIEND, strength=0.5)
        
        # 添加互动（两个参与者）
        interaction_id = social.add_interaction(InteractionType.HELP, [1, 2])
        
        # 完成互动
        social.complete_interaction(interaction_id, outcome=0.8)
        
        # 检查互动
        assert interaction_id not in social.active_interactions
        assert len(social.interaction_history) == 1
        assert social.interaction_history[0].outcome == 0.8
        
        # 检查关系更新
        relationship = social.get_relationship(1)
        assert relationship.strength > 0.5  # 正面互动增加关系强度
    
    def test_social_summary(self):
        """测试社会摘要"""
        social = SocialManagerComponent()
        
        # 添加一些数据
        social.add_relationship(1, RelationshipType.FRIEND)
        social.add_role(SocialRole.TEACHER)
        social.add_status(SocialStatus.EXPERT, level=0.8)
        
        # 获取社会摘要
        summary = social.get_social_summary()
        
        # 检查摘要
        assert summary['relationships_count'] == 1
        assert 'TEACHER' in summary['current_roles']
        assert summary['overall_status'] > 0.5
        assert 'social_influence' in summary


class TestCognitiveComponent:
    """认知组件测试"""
    
    def test_cognitive_initialization(self):
        """测试认知组件初始化"""
        cognitive = CognitiveComponent()
        
        # 检查学习系统
        assert cognitive.learning_style == LearningStyle.BALANCED
        assert cognitive.learning_ability == 0.5
        assert len(cognitive.skills) == 0
        assert len(cognitive.knowledge) == 0
        
        # 检查决策系统
        assert cognitive.decision_style == DecisionStyle.BALANCED
        assert cognitive.risk_preference == RiskPreference.BALANCED
        assert len(cognitive.decision_history) == 0
        
        # 检查问题解决
        assert len(cognitive.active_problems) == 0
        assert cognitive.problem_solving_ability == 0.5
        
        # 检查理解系统
        assert cognitive.comprehension_level == 0.5
        assert cognitive.abstraction_ability == 0.5
        assert cognitive.logical_thinking == 0.5
        assert cognitive.creative_thinking == 0.5
        
        # 检查注意力
        assert cognitive.attention_span == 0.5
        assert cognitive.focus_ability == 0.5
    
    def test_learn_skill(self):
        """测试学习技能"""
        cognitive = CognitiveComponent()
        
        # 学习技能
        cognitive.learn_skill("cooking", practice_amount=0.2)
        
        # 检查技能
        assert "cooking" in cognitive.skills
        assert cognitive.skills["cooking"].proficiency > 0.0
        assert cognitive.skills["cooking"].practice_count == 1
        
        # 获取技能熟练度
        proficiency = cognitive.get_skill_proficiency("cooking")
        assert proficiency > 0.0
    
    def test_add_knowledge(self):
        """测试添加知识"""
        cognitive = CognitiveComponent()
        
        # 添加知识
        cognitive.add_knowledge("mathematics", level=0.3)
        
        # 检查知识
        assert "mathematics" in cognitive.knowledge
        assert cognitive.knowledge["mathematics"] == 0.3
        
        # 获取知识水平
        level = cognitive.get_knowledge_level("mathematics")
        assert level == 0.3
    
    def test_make_decision(self):
        """测试做出决策"""
        cognitive = CognitiveComponent()
        
        # 做出决策
        problem = "去哪里吃饭？"
        options = ["餐厅A", "餐厅B", "餐厅C"]
        
        decision_id = cognitive.make_decision(problem, options)
        
        # 检查决策
        assert len(cognitive.decision_history) == 1
        decision = cognitive.decision_history[0]
        assert decision.decision_id == decision_id
        assert decision.problem == problem
        assert decision.options == options
        assert decision.chosen_option in options
        assert decision.confidence > 0.0
    
    def test_solve_problem(self):
        """测试解决问题"""
        cognitive = CognitiveComponent()
        
        # 解决问题
        problem_description = "如何提高工作效率？"
        problem_id = cognitive.solve_problem(problem_description, complexity=0.6, urgency=0.7)
        
        # 检查问题
        assert problem_id in cognitive.active_problems
        problem = cognitive.active_problems[problem_id]
        assert problem.description == problem_description
        assert problem.complexity == 0.6
        assert problem.urgency == 0.7
        assert len(problem.solutions) > 0
    
    def test_update_cognition(self):
        """测试更新认知"""
        cognitive = CognitiveComponent()
        
        # 学习技能
        cognitive.learn_skill("programming", practice_amount=0.3)
        initial_proficiency = cognitive.get_skill_proficiency("programming")
        
        # 更新认知
        cognitive.update_cognition(1.0)
        
        # 检查技能衰减
        assert cognitive.get_skill_proficiency("programming") < initial_proficiency
    
    def test_cognitive_summary(self):
        """测试认知摘要"""
        cognitive = CognitiveComponent()
        
        # 添加一些数据
        cognitive.learn_skill("writing")
        cognitive.add_knowledge("history")
        cognitive.make_decision("测试问题", ["选项1", "选项2"])
        
        # 获取认知摘要
        summary = cognitive.get_cognitive_summary()
        
        # 检查摘要
        assert summary['learning_style'] == 'BALANCED'
        assert summary['skills_count'] == 1
        assert summary['knowledge_count'] == 1
        assert summary['decisions_made'] == 1
        assert 'problem_solving_ability' in summary


class TestPerceptionComponent:
    """感知组件测试"""
    
    def test_perception_initialization(self):
        """测试感知组件初始化"""
        perception = PerceptionComponent()
        
        # 检查视觉系统
        assert perception.vision_type == VisionType.NORMAL
        assert perception.vision_range == 20.0
        assert perception.vision_acuity == 0.8
        assert len(perception.visible_entities) == 0
        
        # 检查听觉系统
        assert perception.hearing_type == HearingType.NORMAL
        assert perception.hearing_range == 15.0
        assert perception.hearing_acuity == 0.7
        assert len(perception.audible_sounds) == 0
        
        # 检查空间认知
        assert perception.spatial_awareness == SpatialAwareness.BASIC
        assert len(perception.spatial_memory) == 0
        assert perception.current_map is None
        
        # 检查感知整合
        assert perception.attention_focus is None
        assert perception.threat_level == 0.0
        assert perception.opportunity_level == 0.0
    
    def test_update_vision(self):
        """测试更新视觉"""
        perception = PerceptionComponent()
        perception.update_spatial_map((0, 0), 20.0)
        
        # 更新视觉
        entities = [
            (1, (5, 5), 1.0, "brown", "human", (0, 0)),
            (2, (10, 10), 1.0, "black", "animal", (1, 1)),  # 距离14.14，在范围内
            (3, (25, 25), 1.0, "gray", "rock", (0, 0))  # 超出范围
        ]
        
        perception.update_vision(entities)
        
        # 检查可见实体
        assert len(perception.visible_entities) == 2  # 只有2个在范围内
        assert 1 in perception.visible_entities
        assert 2 in perception.visible_entities
        assert 3 not in perception.visible_entities
    
    def test_update_hearing(self):
        """测试更新听觉"""
        perception = PerceptionComponent()
        
        # 更新听觉
        sounds = [
            ("wind", 0.2, 45.0, 5.0, 500),
            ("animal", 0.5, 180.0, 8.0, 800),
            ("human", 0.7, 270.0, 20.0, 300)  # 超出范围
        ]
        
        perception.update_hearing(sounds)
        
        # 检查可听声音
        assert len(perception.audible_sounds) == 2  # 只有2个在范围内
        assert perception.audible_sounds[0].sound_type == "wind"
        assert perception.audible_sounds[1].sound_type == "animal"
    
    def test_assess_threats(self):
        """测试评估威胁"""
        perception = PerceptionComponent()
        perception.update_spatial_map((0, 0), 20.0)
        
        # 添加威胁实体
        entities = [
            (1, (5, 5), 2.0, "red", "predator", (1, 1)),  # 威胁
            (2, (10, 10), 0.5, "brown", "prey", (0, 0))   # 非威胁
        ]
        
        perception.update_vision(entities)
        
        # 评估威胁
        threat_level = perception.assess_threats()
        
        # 检查威胁水平
        assert 0.0 <= threat_level <= 1.0
        
        # 获取最近威胁
        nearest_threat = perception.get_nearest_threat()
        assert nearest_threat is not None
        assert nearest_threat.entity_id == 1
    
    def test_assess_opportunities(self):
        """测试评估机会"""
        perception = PerceptionComponent()
        perception.update_spatial_map((0, 0), 20.0)
        
        # 添加资源
        perception.add_resource((5, 5))
        perception.add_resource((10, 10))
        
        # 评估机会
        opportunity_level = perception.assess_opportunities()
        
        # 检查机会水平
        assert 0.0 <= opportunity_level <= 1.0
        
        # 获取最近资源
        nearest_resource = perception.get_nearest_resource()
        assert nearest_resource is not None
    
    def test_get_safe_position(self):
        """测试获取安全位置"""
        perception = PerceptionComponent()
        perception.update_spatial_map((0, 0), 20.0)
        
        # 添加威胁实体
        entities = [
            (1, (5, 5), 2.0, "red", "predator", (1, 1))  # 威胁
        ]
        
        perception.update_vision(entities)
        
        # 获取安全位置
        current_position = (0, 0)
        safe_position = perception.get_safe_position(current_position)
        
        # 检查安全位置
        assert safe_position is not None
        assert safe_position != current_position
    
    def test_update_perception(self):
        """测试更新感知"""
        perception = PerceptionComponent()
        perception.update_spatial_map((0, 0), 20.0)
        
        # 添加一些数据
        entities = [(1, (5, 5), 1.0, "brown", "human", (0, 0))]
        perception.update_vision(entities)
        
        # 更新感知
        perception.update_perception(1.0)
        
        # 检查感知历史
        assert len(perception.perception_history) == 1
        assert perception.perception_history[0]['visible_entities'] == 1
    
    def test_perception_summary(self):
        """测试感知摘要"""
        perception = PerceptionComponent()
        
        # 添加一些数据
        perception.update_spatial_map((0, 0), 20.0)
        entities = [(1, (5, 5), 1.0, "brown", "human", (0, 0))]
        perception.update_vision(entities)
        
        # 获取感知摘要
        summary = perception.get_perception_summary()
        
        # 检查摘要
        assert summary['vision_type'] == 'NORMAL'
        assert summary['visible_entities'] == 1
        assert 'threat_level' in summary
        assert 'opportunity_level' in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
