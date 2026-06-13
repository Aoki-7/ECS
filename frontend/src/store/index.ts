/**
 * 全局状态管理 (Zustand)
 * 
 * 版本: v4.0
 */

import { create } from 'zustand'
import { WorldStats, Entity, SystemInfo } from '../types'

interface WorldState {
  // World 状态
  stats: WorldStats | null
  entities: Entity[]
  systems: SystemInfo[]
  
  // 模拟状态
  running: boolean
  paused: boolean
  tick: number
  
  // 选中状态
  selectedEntity: number | null
  
  // 动作
  setStats: (stats: WorldStats) => void
  setEntities: (entities: Entity[]) => void
  setSystems: (systems: SystemInfo[]) => void
  setRunning: (running: boolean) => void
  setPaused: (paused: boolean) => void
  setTick: (tick: number) => void
  setSelectedEntity: (id: number | null) => void
}

export const useWorldStore = create<WorldState>((set) => ({
  stats: null,
  entities: [],
  systems: [],
  running: false,
  paused: false,
  tick: 0,
  selectedEntity: null,
  
  setStats: (stats) => set({ stats }),
  setEntities: (entities) => set({ entities }),
  setSystems: (systems) => set({ systems }),
  setRunning: (running) => set({ running }),
  setPaused: (paused) => set({ paused }),
  setTick: (tick) => set({ tick }),
  setSelectedEntity: (id) => set({ selectedEntity: id }),
}))
