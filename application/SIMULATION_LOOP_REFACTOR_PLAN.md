# SimulationLoop 拆分策略

## 当前问题
- `simulation_loop.py` 899行，职责过重
- 承担：导入管理、初始化、系统注册、资源生成、人口创建、主循环、统计

## 拆分方案

### 1. SystemRegistry（系统注册中心）
- 负责所有系统的导入和注册
- 按层级分组：基础设施、环境、人类、动物、植物、生态、文明

### 2. EntitySpawner（实体生成器）
- 初始资源生成（食物、水源）
- 初始人口创建
- 初始植物创建
- 环境网格初始化

### 3. SimulationDriver（模拟驱动器）
- 主循环 `run_simulation()`
- 单步更新 `update()`
- 统计信息 `get_stats()`
- 资源再生 `_regenerate_resources()`

### 4. SimulationLoop（保留）
- 组合以上三个组件
- 提供统一入口

## 实施步骤
1. 创建 `application/system_registry.py`
2. 创建 `application/entity_spawner.py`
3. 创建 `application/simulation_driver.py`
4. 重写 `simulation_loop.py` 为组合模式
5. 测试适配
