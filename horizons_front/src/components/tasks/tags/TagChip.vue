<template>
  <span
    class="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium border whitespace-nowrap"
    :style="{ background: tag.color + '22', borderColor: tag.color + '44', color: tag.color }"
  >{{ tag.name }}</span>
</template>

<script setup lang="ts">
import type { Tag } from '../../../types/task.types'
defineProps<{ tag: Tag }>()
</script>