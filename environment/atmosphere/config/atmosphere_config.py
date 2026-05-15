#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
大气系统配置模块

支持通过配置文件调整：
1. 子系统优先级顺序
2. 参数基值/增长因子
3. 启用/禁用特定功能
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
import os


@dataclass
class SubsystemConfig:
    """子系统配置"""
    name: str
    priority: float = 100.0       # 优先级（越小越先执行）
    enabled: bool = True          # 是否启用
    params: Dict[str, float] = field(default_factory=dict)


@dataclass
class AtmosphereConfig:
    """大气系统主配置"""
    
    # 基础物理参数
    sea_level_pressure: float = 1013.25   # hPa
    lapse_rate: float = 6.5e-3            # °C/m（温度递减率）
    gas_constant: float = 287.05          # J/(kg·K)，空气气体常数
    
    # 湿度参数
    saturation_pressure_slope: float = 0.6  # °C 下饱和蒸气压变化斜率（简化模型）
    
    # 子系统列表
    subsystems: List[SubsystemConfig] = field(
        default_factory=lambda: [
            SubsystemConfig("pressure", priority=130, enabled=True),
            SubsystemConfig("thermodynamics", priority=130, enabled=True),
            SubsystemConfig("cloud", priority=140, enabled=True),
            SubsystemConfig("wind", priority=150, enabled=True),
            SubsystemConfig("convection", priority=160, enabled=True),
        ]
    )
    
    # 日志级别：debug / info / warn / error
    log_level: str = "info"

    def to_dict(self) -> Dict:
        """序列化为字典"""
        return {
            "sea_level_pressure": self.sea_level_pressure,
            "lapse_rate": self.lapse_rate,
            "gas_constant": self.gas_constant,
            "subsystems": [
                {"name": s.name, "priority": s.priority, "enabled": s.enabled}
                for s in self.subsystems
            ],
            "log_level": self.log_level,
        }

    def load_from_dict(self, data: Dict):
        """从字典加载配置"""
        if "sea_level_pressure" in data:
            self.sea_level_pressure = data["sea_level_pressure"]
        if "lapse_rate" in data:
            self.lapse_rate = data["lapse_rate"]
        if "subsystems" in data:
            for s_config in data["subsystems"]:
                for s in self.subsystems:
                    if s.name == s_config.get("name"):
                        s.priority = s_config.get("priority", s.priority)
                        s.enabled = s_config.get("enabled", s.enabled)

    def save_to_file(self, filepath: Optional[str] = None):
        """保存配置文件"""
        if filepath is None:
            # 默认保存到 environment/atmosphere/config/atmosphere.json
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            filepath = os.path.join(base_dir, "environment", "atmosphere", "config", "atmosphere.json")
        
        data = self.to_dict()
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json_str)

    @classmethod
    def from_file(cls, filepath: Optional[str] = None, override: Optional[Dict] = None):
        """从文件加载配置"""
        if filepath is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            filepath = os.path.join(base_dir, "environment", "atmosphere", "config", "atmosphere.json")
        
        if not os.path.exists(filepath):
            print(f"配置文件不存在：{filepath}，使用默认配置")
            return cls()
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        config = cls()
        config.load_from_dict(data)
        
        # 如有 override 参数，应用覆盖
        if override:
            for k, v in override.items():
                setattr(config, k, v)
        
        return config


class AtmosphereConfigManager:
    """配置管理器：提供全局配置访问"""
    
    _instance = None
    
    def __init__(self):
        if AtmosphereConfigManager._instance is not None:
            raise RuntimeError("AtmosphereConfigManager 已实例化，请直接从 AtmosphereSystem 获取_config")
        self._config = AtmosphereConfig()
    
    @classmethod
    def get(cls) -> "AtmosphereConfigManager":
        """单例获取"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @property
    def config(self) -> AtmosphereConfig:
        """返回当前配置对象"""
        return self._config
    
    def set_config(self, config: AtmosphereConfig):
        """设置新配置"""
        self._config = config
    
    def reload_from_file(self, filepath: str):
        """从文件重新加载配置"""
        self._config.load_from_dict(json.loads(open(filepath, 'r', encoding='utf-8').read()))
