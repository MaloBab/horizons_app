<template>
  <div class="flex flex-col gap-1.5">
    <label
      :for="id"
      class="text-xs font-medium tracking-wide transition-colors duration-200"
      :class="isFocused ? 'text-cyan-400' : 'text-slate-400'"
    >
      {{ label }}
    </label>

    <div
      class="flex items-center gap-2.5 px-3.5 rounded-xl border bg-slate-800/50 backdrop-blur-sm transition-all duration-200"
      :class="[
        error
          ? 'border-red-500/50 bg-red-500/5'
          : isFocused
          ? 'border-cyan-500/50 shadow-[0_0_0_3px_rgba(6,182,212,0.08)]'
          : 'border-white/10 hover:border-white/20',
      ]"
    >
      <span
        class="flex items-center shrink-0 transition-colors duration-200"
        :class="isFocused ? 'text-cyan-400/70' : 'text-slate-500'"
      >
        <slot name="icon" />
      </span>

      <input
        :id="id"
        :type="currentType"
        :value="modelValue"
        :placeholder="placeholder"
        :autocomplete="autocomplete"
        class="flex-1 bg-transparent border-none outline-none text-white text-sm placeholder:text-slate-600 py-3 caret-cyan-400"
        @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        @focus="isFocused = true"
        @blur="isFocused = false"
      />

      <button
        v-if="type === 'password'"
        type="button"
        tabindex="-1"
        class="shrink-0 text-slate-500 hover:text-slate-300 transition-colors duration-200 cursor-pointer p-0 bg-transparent border-none"
        @click="showPassword = !showPassword"
      >
        <svg v-if="!showPassword" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
        </svg>
        <svg v-else class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
          <line x1="1" y1="1" x2="23" y2="23"/>
        </svg>
      </button>
    </div>

    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-1"
      leave-active-class="transition-all duration-150 ease-in"
      leave-to-class="opacity-0 -translate-y-1"
    >
      <p v-if="error" class="text-xs text-red-400">{{ error }}</p>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  id: string
  label: string
  modelValue: string
  type?: string
  placeholder?: string
  autocomplete?: string
  error?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  placeholder: '',
  autocomplete: 'off',
  error: '',
})

const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

const isFocused = ref(false)
const showPassword = ref(false)
const currentType = computed(() =>
  props.type === 'password' ? (showPassword.value ? 'text' : 'password') : props.type,
)
</script>