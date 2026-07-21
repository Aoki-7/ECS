import React, { useRef, useEffect, useCallback } from 'react'

export interface EntitySnapshot {
  id: number
  x: number
  y: number
  type: string
  state?: Record<string, any>
}

export interface WorldSnapshot {
  type: string
  tick: number
  config: {
    width: number
    height: number
    time_scale: number
    speed: number
    paused: boolean
  }
  entities: EntitySnapshot[]
  stats: Record<string, number | boolean>
}

const TYPE_COLORS: Record<string, string> = {
  human: '#f5e6d3',
  plant: '#4caf50',
  animal: '#9c27b0',
  food: '#ff9800',
  water: '#2196f3',
  building: '#795548',
  corpse: '#424242',
  unknown: '#9e9e9e',
}

interface PixelCanvasProps {
  snapshot: WorldSnapshot | null
  scale?: number
  onEntityClick?: (entity: EntitySnapshot) => void
}

const PixelCanvas: React.FC<PixelCanvasProps> = ({
  snapshot,
  scale = 8,
  onEntityClick,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  const draw = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas || !snapshot) return

    const width = snapshot.config.width
    const height = snapshot.config.height
    canvas.width = width * scale
    canvas.height = height * scale

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // 像素风：关闭平滑
    ctx.imageSmoothingEnabled = false

    // 背景
    ctx.fillStyle = '#1a1a1a'
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    // 可选：网格线
    ctx.strokeStyle = '#2a2a2a'
    ctx.lineWidth = 1
    for (let x = 0; x <= width; x++) {
      ctx.beginPath()
      ctx.moveTo(x * scale, 0)
      ctx.lineTo(x * scale, canvas.height)
      ctx.stroke()
    }
    for (let y = 0; y <= height; y++) {
      ctx.beginPath()
      ctx.moveTo(0, y * scale)
      ctx.lineTo(canvas.width, y * scale)
      ctx.stroke()
    }

    // 按类型分组绘制，避免同位置重叠完全覆盖时无法区分
    // 先画静态资源，再画植物，最后画人类/动物
    const order = ['water', 'food', 'plant', 'animal', 'building', 'corpse', 'human', 'unknown']
    const byType: Record<string, EntitySnapshot[]> = {}
    for (const e of snapshot.entities) {
      const t = e.type || 'unknown'
      if (!byType[t]) byType[t] = []
      byType[t].push(e)
    }

    for (const t of order) {
      const entities = byType[t] || []
      for (const e of entities) {
        const color = TYPE_COLORS[t] || TYPE_COLORS.unknown
        ctx.fillStyle = color
        ctx.fillRect(e.x * scale, e.y * scale, scale, scale)

        // 高亮边框
        ctx.strokeStyle = 'rgba(0,0,0,0.3)'
        ctx.lineWidth = 1
        ctx.strokeRect(e.x * scale, e.y * scale, scale, scale)
      }
    }
  }, [snapshot, scale])

  useEffect(() => {
    draw()
  }, [draw])

  const handleClick = useCallback(
    (evt: React.MouseEvent<HTMLCanvasElement>) => {
      if (!snapshot || !onEntityClick) return
      const canvas = canvasRef.current
      if (!canvas) return

      const rect = canvas.getBoundingClientRect()
      const x = Math.floor((evt.clientX - rect.left) / scale)
      const y = Math.floor((evt.clientY - rect.top) / scale)

      // 找该位置最上层的实体（人类优先）
      const candidates = snapshot.entities.filter(
        (e) => e.x === x && e.y === y
      )
      if (candidates.length === 0) return
      const priority = ['human', 'animal', 'plant', 'food', 'water', 'building', 'unknown']
      let chosen = candidates[0]
      let chosenIdx = priority.indexOf(chosen.type)
      for (const e of candidates) {
        const idx = priority.indexOf(e.type)
        if (idx < chosenIdx) {
          chosen = e
          chosenIdx = idx
        }
      }
      onEntityClick(chosen)
    },
    [snapshot, scale, onEntityClick]
  )

  return (
    <canvas
      ref={canvasRef}
      onClick={handleClick}
      style={{
        imageRendering: 'pixelated',
        cursor: 'crosshair',
        boxShadow: '0 0 0 2px #333',
      }}
    />
  )
}

export default PixelCanvas
