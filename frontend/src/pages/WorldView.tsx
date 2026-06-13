import { useEffect, useRef } from 'react'
import './WorldView.css'

function WorldView() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // 设置画布大小
    const resize = () => {
      canvas.width = canvas.offsetWidth
      canvas.height = canvas.offsetHeight
    }
    resize()
    window.addEventListener('resize', resize)

    // 绘制网格
    const drawGrid = () => {
      ctx.fillStyle = '#1a1a2e'
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      ctx.strokeStyle = '#0f3460'
      ctx.lineWidth = 1

      const gridSize = 50
      for (let x = 0; x < canvas.width; x += gridSize) {
        ctx.beginPath()
        ctx.moveTo(x, 0)
        ctx.lineTo(x, canvas.height)
        ctx.stroke()
      }
      for (let y = 0; y < canvas.height; y += gridSize) {
        ctx.beginPath()
        ctx.moveTo(0, y)
        ctx.lineTo(canvas.width, y)
        ctx.stroke()
      }
    }

    // 动画循环
    let animationId: number
    const animate = () => {
      drawGrid()
      // TODO: 绘制实体
      animationId = requestAnimationFrame(animate)
    }
    animate()

    return () => {
      window.removeEventListener('resize', resize)
      cancelAnimationFrame(animationId)
    }
  }, [])

  return (
    <div className="world-view">
      <div className="toolbar">
        <button>▶ 运行</button>
        <button>⏸ 暂停</button>
        <button>⏭ 步进</button>
        <span className="tick">Tick: 0</span>
      </div>
      <canvas ref={canvasRef} className="world-canvas" />
      <div className="info-panel">
        <h3>世界信息</h3>
        <p>实体数量: 0</p>
        <p>系统数量: 0</p>
        <p>FPS: 60</p>
      </div>
    </div>
  )
}

export default WorldView
