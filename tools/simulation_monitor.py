import sys
import time
import logging
import gc
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入核心模块
from core.world import World
from application.simulation_loop import SimulationLoop

# 创建世界
logger.info('=== 创建世界 ===')
world = World()

# 创建模拟循环
logger.info('=== 创建模拟循环 ===')
sim = SimulationLoop(world)

# 初始化
logger.info('=== 初始化模拟 ===')
sim.init()
sim.create_initial_resources(food_count=80, water_count=80)
sim.create_initial_plants(plant_count=30)
sim.create_initial_population(human_count=10)

# 监控数据
monitor_data = []
start_time = time.time()
max_ticks = 1000

logger.info(f'=== 开始模拟 {max_ticks} ticks ===')

for tick in range(max_ticks):
    # 执行 tick
    sim.update()
    
    # 每 100 ticks 记录一次监控数据
    if tick % 100 == 0:
        entity_count = len(world._entities) if hasattr(world, '_entities') else 0
        active_count = sum(1 for e in world._entities.values() if hasattr(e, '_is_active') and e._is_active) if hasattr(world, '_entities') else 0
        
        # 获取系统状态
        system_count = len(world._systems) if hasattr(world, '_systems') else 0
        
        # 获取内存使用（粗略估计）
        gc.collect()
        obj_count = len(gc.get_objects())
        
        elapsed = time.time() - start_time
        tps = tick / elapsed if elapsed > 0 else 0
        
        data = {
            'tick': tick,
            'entities': entity_count,
            'active': active_count,
            'systems': system_count,
            'objects': obj_count,
            'tps': tps,
            'elapsed': elapsed,
        }
        monitor_data.append(data)
        
        logger.info(f'Tick {tick:5d} | Entities: {entity_count:5d} | Active: {active_count:5d} | Systems: {system_count:3d} | Objects: {obj_count:8d} | TPS: {tps:6.1f} | Elapsed: {elapsed:6.2f}s')
        
        # 检查是否异常增长
        if tick > 0 and entity_count > 10000:
            logger.warning(f'实体数异常增长: {entity_count}')
            break
        
        if tps < 1.0 and tick > 100:
            logger.warning(f'TPS 过低: {tps:.1f}')
            break

logger.info('=== 模拟完成 ===')

# 汇总
logger.info('=== 监控汇总 ===')
if monitor_data:
    first = monitor_data[0]
    last = monitor_data[-1]
    
    entity_growth = last['entities'] - first['entities']
    obj_growth = last['objects'] - first['objects']
    
    logger.info(f'实体数变化: {first["entities"]} -> {last["entities"]} ({entity_growth:+,d})')
    logger.info(f'对象数变化: {first["objects"]} -> {last["objects"]} ({obj_growth:+,d})')
    logger.info(f'平均 TPS: {sum(d["tps"] for d in monitor_data) / len(monitor_data):.1f}')
    logger.info(f'总运行时间: {last["elapsed"]:.2f}s')
    
    # 检查增长趋势
    if entity_growth > 1000:
        logger.warning('实体数增长过快，可能存在内存泄漏')
    elif entity_growth > 0:
        logger.info('实体数正常增长')
    else:
        logger.info('实体数稳定')
    
    if obj_growth > 100000:
        logger.warning('对象数增长过快，可能存在内存泄漏')
    else:
        logger.info('对象数增长正常')
