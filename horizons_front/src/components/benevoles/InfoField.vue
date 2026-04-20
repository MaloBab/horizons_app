<template>
  <div class="bg-slate-700/30 rounded-lg p-1.5 border border-slate-600/50">
    <div class="flex items-start gap-3">
      <component :is="iconComponent" class="w-5 h-5 mt-0.5 shrink-0" :class="iconColor"/>
      <div class="flex-1 min-w-0">
        <p class="text-slate-400 text-sm mb-1">{{ label }}</p>
        <p class="text-white font-medium wrap-break-word">{{ value }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Mail, Phone, MapPin } from 'lucide-vue-next'

interface Props {
  label: string
  value: string
  icon?: 'mail' | 'phone' | 'map-pin'
}

const props = defineProps<Props>()

const iconComponent = computed(() => {
  const icons = {
    'mail': Mail,
    'phone': Phone,
    'map-pin': MapPin,
  }
  return icons[props.icon!]
})

const iconColor = computed(() => {
  const colors = {
    'mail': 'text-blue-400',
    'phone': 'text-green-400',
    'map-pin': 'text-purple-400',
  }
  return colors[props.icon!]
})
</script>