
from dataclasses import dataclass
from typing import Optional


@dataclass
class Trait:
    """
    Trait 表示“基因表达后的数值性状”。

    它是 Genome → Gene 表达之后的中间层结果，
    由 GeneExpressionSystem 写入，
    被 GrowthSystem / EnvironmentSystem 等系统读取。

    ⚠ 注意：
    - Trait 不是基因本身
    - Trait 是“当前表达状态”
    - 每一帧都可能被重新计算
    """

    # 性状名称（例如: growth_rate, leaf_size）
    name: str

    # 当前表达值
    value: float

    # 可选：下界约束（防止出现物理不合理值）
    min_value: Optional[float] = None

    # 可选：上界约束
    max_value: Optional[float] = None

    # 来源标记：
    # gene         -> 基因表达
    # environment  -> 环境调制
    # mutation     -> 突变产生
    # system       -> 其他系统动态修改
    source: str = "gene"

    # 是否启用自动约束
    auto_clamp: bool = True

    # 可选：表达权重（用于后期做 dominance / 环境调制）
    weight: float = 1.0

    # 是否允许被系统修改（用于区分“遗传性状”和“临时性状”）
    mutable: bool = True

    def apply_delta(self, delta: float):
        """
        对 Trait 进行增量修改。

        常用于：
        - 环境调制
        - 突变叠加
        - 系统动态影响
        """
        if not self.mutable:
            return

        self.value += delta

        if self.auto_clamp:
            self.clamp()

    def clamp(self):
        """
        将 value 限制在 min_value / max_value 范围内。
        用于防止：
        - 负生长率
        - 无限增长
        - 非物理数值
        """
        if self.min_value is not None:
            self.value = max(self.min_value, self.value)

        if self.max_value is not None:
            self.value = min(self.max_value, self.value)

    def reset(self, new_value: float):
        """
        重置数值（通常在每帧基因重新表达时使用）。
        """
        self.value = new_value
        if self.auto_clamp:
            self.clamp()

    def copy(self):
        """
        返回 Trait 的拷贝。
        用于：
        - 代际遗传
        - 快照
        """
        return Trait(
            name=self.name,
            value=self.value,
            min_value=self.min_value,
            max_value=self.max_value,
            source=self.source,
            auto_clamp=self.auto_clamp,
            weight=self.weight,
            mutable=self.mutable
        )
