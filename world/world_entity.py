


# simulation/world/world_entity.py

class WorldEntity:
    """
    世界级单例实体
    只允许挂世界级组件
    """

    __slots__ = ("_components",)

    def __init__(self):
        self._components = {}

    def add_component(self, component):
        self._components[type(component)] = component

    def add_components(self, *components):
        """
        批量添加组件
        """
        for component in components:
            self.add_component(component)

    def get_component(self, component_type):
        return self._components.get(component_type)

    def get_components(self, *component_types):
        """
        批量获取组件

        返回 tuple，与输入顺序一致
        """
        return tuple(self.get_component(t) for t in component_types)

    def get_components_dict(self, *component_types):
        """
        批量获取组件（字典形式）
        """
        return {t: self.get_component(t) for t in component_types}
    
    def get_all_components(self):
        """
        获取所有组件实例（list）
        """
        return list(self._components.values())

    def get_all_component_types(self):
        """
        获取所有组件类型
        """
        return list(self._components.keys())
    
    def get_all_components_dict(self):
        """
        获取完整组件字典（type -> instance）
        """
        return dict(self._components)
    
    def has_component(self, component_type):
        return component_type in self._components
    
    def has_components(self, *component_types):
        """
        是否同时拥有多个组件
        """
        return all(self.has_component(t) for t in component_types)
    
    def require_components(self, *component_types):
        comps = []
        for t in component_types:
            c = self.get_component(t)
            if c is None:
                raise RuntimeError(f"WorldEntity missing component: {t.__name__}")
            comps.append(c)
        return tuple(comps)

    def iter_components(self):
        return self._components.values()