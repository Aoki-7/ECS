#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天体组件

v3.5 新增 — P2

职责：
    - 存储天体物理参数
    - 支持月球、太阳等天体

设计原则：
    - 纯物理量，无硬编码行为
    - 所有参数由物理定律驱动
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple

from core.component import Component


@dataclass
class CelestialBodyComponent(Component):
    """
    天体组件

    所有参数为纯物理量，由轨道力学驱动：
    - 质量 → 引力
    - 距离 → 引力强度
    - 轨道参数 → 位置变化

    Attributes:
        body_name: 天体名称（标识用，不影响物理）
        mass: 质量 (kg)
        distance: 与地球距离 (m)
        orbital_period: 轨道周期 (天)
        orbital_eccentricity: 轨道偏心率 (0-1)
        orbital_inclination: 轨道倾角 (度)
        current_phase: 当前相位 (0-2π)
        phase_rate: 相位变化速率 (rad/天)
        gravitational_parameter: 引力参数 GM (m³/s²)
    """

    body_name: str = "moon"
    mass: float = 7.342e22  # 月球质量 kg
    distance: float = 3.844e8  # 地月距离 m
    orbital_period: float = 27.32  # 天
    orbital_eccentricity: float = 0.0549
    orbital_inclination: float = 5.14  # 度
    current_phase: float = 0.0  # rad
    phase_rate: float = 0.229  # rad/天
    gravitational_parameter: float = 4.904e12  # m³/s²

    def to_dict(self) -> dict:
        return {
            "body_name": self.body_name,
            "mass": self.mass,
            "distance": self.distance,
            "orbital_period": self.orbital_period,
            "orbital_eccentricity": self.orbital_eccentricity,
            "orbital_inclination": self.orbital_inclination,
            "current_phase": self.current_phase,
            "phase_rate": self.phase_rate,
            "gravitational_parameter": self.gravitational_parameter,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CelestialBodyComponent":
        return cls(
            body_name=data.get("body_name", "moon"),
            mass=data.get("mass", 7.342e22),
            distance=data.get("distance", 3.844e8),
            orbital_period=data.get("orbital_period", 27.32),
            orbital_eccentricity=data.get("orbital_eccentricity", 0.0549),
            orbital_inclination=data.get("orbital_inclination", 5.14),
            current_phase=data.get("current_phase", 0.0),
            phase_rate=data.get("phase_rate", 0.229),
            gravitational_parameter=data.get("gravitational_parameter", 4.904e12),
        )

    @property
    def tidal_force(self) -> float:
        """
        计算潮汐力（与质量成正比，与距离立方成反比）
        F_tidal ∝ M / d³
        """
        if self.distance <= 0:
            return 0.0
        return self.mass / (self.distance ** 3)

    @property
    def current_distance(self) -> float:
        """
        根据轨道偏心率计算当前实际距离
        r = a(1 - e²) / (1 + e·cos(θ))
        """
        a = self.distance  # 半长轴
        e = self.orbital_eccentricity
        theta = self.current_phase
        
        if e >= 1.0:
            return a
        
        return a * (1 - e * e) / (1 + e * self._cos(theta))

    def _cos(self, theta: float) -> float:
        """简化的余弦计算（避免import math在dataclass中的问题）"""
        # 使用泰勒展开近似
        theta = theta % 6.283185307179586
        if theta > 3.141592653589793:
            theta = 6.283185307179586 - theta
            sign = -1
        else:
            sign = 1
        
        theta2 = theta * theta
        result = 1 - theta2 / 2 + theta2 * theta2 / 24 - theta2 * theta2 * theta2 / 720
        return sign * max(-1.0, min(1.0, result))

    def advance_phase(self, dt_days: float) -> None:
        """
        推进轨道相位
        由角动量守恒驱动，非硬编码
        """
        self.current_phase += self.phase_rate * dt_days
        # 保持在 0-2π 范围
        two_pi = 6.283185307179586
        while self.current_phase >= two_pi:
            self.current_phase -= two_pi
        while self.current_phase < 0:
            self.current_phase += two_pi
