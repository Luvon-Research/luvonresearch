<template>
    <canvas ref="canvas" class="dots-bg" />
  </template>
  
  <script setup>
  import { ref, onMounted, onBeforeUnmount } from 'vue'
  
  const canvas       = ref(null)
  let ctx
  let cols, rows, spacing, width, height
  let brightness = []
  let timeCounter = 0
  
  // ↓ lowered from 0.05 → 0.025 for a much slower ping-pong
  const waveSpeed     = 0.025  
  const fadeFactor    = 0.96  
  const smoothW       = 8     
  const peakIntensity = 0.96  
  
  let animId
  
  function init() {
    width   = window.innerWidth
    height  = window.innerHeight
    spacing = 40
    cols    = Math.ceil(width / spacing)
    rows    = Math.ceil(height / spacing)
  
    canvas.value.width  = width
    canvas.value.height = height
    ctx = canvas.value.getContext('2d')
  
    brightness = Array.from({ length: rows }, () =>
      new Array(cols).fill(0)
    )
  
    timeCounter = 0
  }
  
  function animate() {
    // advance our sine-time more slowly
    timeCounter += waveSpeed
    // map sine [–1..1] → [0..rows/2]
    const wavePos = ((Math.sin(timeCounter) + 1) / 2) * (rows / 2)
  
    // update brightness grid
    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < cols; x++) {
        let b = brightness[y][x] * fadeFactor
        const dTop    = Math.abs(y - wavePos)
        const dBottom = Math.abs((rows - 1 - y) - wavePos)
        const peakTop    = Math.max(0, 1 - dTop    / smoothW)
        const peakBottom = Math.max(0, 1 - dBottom / smoothW)
        const peak       = Math.max(peakTop, peakBottom) * peakIntensity
  
        brightness[y][x] = Math.max(b, peak)
      }
    }
  
    // draw
    ctx.clearRect(0, 0, width, height)
    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < cols; x++) {
        const b = brightness[y][x]
        if (b > 0.02) {
          const px = x * spacing
          const py = y * spacing
          const r  = 1 + b * 1.5
          ctx.beginPath()
          ctx.arc(px, py, r, 0, 2 * Math.PI)
          ctx.fillStyle = `rgba(0,150,255,${Math.min(1, b * 0.6)})`
          ctx.fill()
        }
      }
    }
  
    animId = requestAnimationFrame(animate)
  }
  
  onMounted(() => {
    init()
    animate()
    window.addEventListener('resize', () => {
      cancelAnimationFrame(animId)
      init()
      animate()
    })
  })
  
  onBeforeUnmount(() => {
    cancelAnimationFrame(animId)
    window.removeEventListener('resize', init)
  })
  </script>
  
  <style>
  .dots-bg {
    position: fixed;
    top: 0;
    left: 0;
    z-index: -1;
    background: #ffffff;
  }
  </style>
  