


from core.component import Component

class EnergyComponent(Component):
    """
        能量组件
    """
    def __init__(self, max_energy: float = 100.0):
        
        self.value = 0.0
        self.growth_pool = 0.0
        self.max_energy = max_energy