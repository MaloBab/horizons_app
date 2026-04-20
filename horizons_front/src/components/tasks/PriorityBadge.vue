<template>
  <div class="flex items-center gap-1.5" :title="cfg.label">
    <component :is="cfg.icon" :style="{ width: `${iconSize}px`, height: `${iconSize}px` }" :class="cfg.cls" />
    <span v-if="showLabel" class="text-xs font-medium" :class="cfg.cls">{{ cfg.label }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArrowDown, Minus, ArrowUp, Zap } from 'lucide-vue-next'
import type { TaskPriority } from '../../types/task.types'

const props = withDefaults(defineProps<{ priority: TaskPriority; showLabel?: boolean; iconSize?: number }>(), { showLabel: false, iconSize: 13 })

const MAP = {
  low:      { icon: ArrowDown, cls: 'text-slate-400',  label: 'Basse'    },
  medium:   { icon: Minus,     cls: 'text-blue-400',   label: 'Moyenne'  },
  high:     { icon: ArrowUp,   cls: 'text-amber-400',  label: 'Haute'    },
  critical: { icon: Zap,       cls: 'text-red-400',    label: 'Critique' },
}
const cfg = computed(() => MAP[props.priority])
</script>