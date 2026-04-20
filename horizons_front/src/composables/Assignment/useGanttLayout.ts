import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import type { Ref } from 'vue'

const COLUMN_WIDTH_MIN = 45
const COLUMN_WIDTH_MAX = 80

export function useGanttLayout(
  ganttContainerRef: Ref<HTMLElement | null>,
  visibleDayCount: Ref<number>,
  colLeftTotal: number,
) {
  const columnWidth = ref(60)

  function recalcColumnWidth() {
    const nbHours = visibleDayCount.value * 22
    if (nbHours === 0 || !ganttContainerRef.value) return

    const availableWidth = ganttContainerRef.value.clientWidth - colLeftTotal
    if (availableWidth <= 0) return

    const raw = Math.floor(availableWidth / nbHours)
    columnWidth.value = Math.min(COLUMN_WIDTH_MAX, Math.max(COLUMN_WIDTH_MIN, raw))
  }

  let resizeObserver: ResizeObserver | null = null

  onMounted(() => {
    recalcColumnWidth()
    if (ganttContainerRef.value) {
      resizeObserver = new ResizeObserver(() => {
        nextTick(() => recalcColumnWidth())
      })
      resizeObserver.observe(ganttContainerRef.value)
    }
  })

  onUnmounted(() => {
    resizeObserver?.disconnect()
    resizeObserver = null
  })

  watch(visibleDayCount, () => recalcColumnWidth(), { flush: 'post' })

  return { columnWidth }
}