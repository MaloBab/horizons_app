<template>
  <div class="relative" ref="btnRef">
    <button
      class="flex flex-col items-center justify-center w-7 h-7 mx-0.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-all cursor-pointer"
      title="Couleur du texte"
      @mousedown.prevent="toggle"
    >
      <span class="text-[11px] font-black leading-none mt-1" style="font-family:serif">A</span>
      <div class="w-4 h-0.75 rounded-full mt-0.5 transition-colors duration-150" :style="{ background: currentColor }" />
    </button>

    <Teleport to="body">
      <div
        v-if="show"
        ref="panelRef"
        class="fixed z-9999 bg-slate-800 border border-white/10 rounded-xl shadow-2xl p-3 flex flex-col gap-2.5 w-56"
        :style="pos"
        @mousedown.stop
      >
        <!-- Preset colors -->
        <div>
          <p class="text-[10px] text-slate-500 font-medium uppercase tracking-wider mb-1.5">Couleurs</p>
          <div class="grid grid-cols-10 gap-1">
            <button
              v-for="c in PRESETS"
              :key="c"
              class="w-4 h-4 rounded-full ring-1 ring-white/10 hover:scale-110 transition-transform"
              :style="{ background: c }"
              :title="c"
              @mousedown.prevent="apply(c)"
            />
          </div>
        </div>

        <!-- Recent colors -->
        <template v-if="recentColors.length">
          <div class="border-t border-white/8 pt-2">
            <p class="text-[10px] text-slate-500 font-medium uppercase tracking-wider mb-1.5">Récentes</p>
            <div class="flex flex-wrap gap-1">
              <button
                v-for="c in recentColors"
                :key="c"
                class="w-4 h-4 rounded-full ring-1 ring-white/10 hover:scale-110 transition-transform"
                :style="{ background: c }"
                :title="c"
                @mousedown.prevent="apply(c)"
              />
            </div>
          </div>
        </template>

        <!-- Custom color picker -->
        <div class="border-t border-white/8 pt-2 flex flex-col gap-2">
          <p class="text-[10px] text-slate-500 font-medium uppercase tracking-wider">Personnalisée</p>

          <!-- Saturation / Brightness box -->
          <div
            ref="sbRef"
            class="relative w-full h-32 rounded-lg select-none"
            :style="{ background: `hsl(${hue}, 100%, 50%)`, cursor: 'crosshair' }"
            @mousedown.prevent="startSB"
          >
            <div class="absolute inset-0 rounded-lg" style="background: linear-gradient(to right, #fff, transparent)" />
            <div class="absolute inset-0 rounded-lg" style="background: linear-gradient(to top, #000, transparent)" />
            <!-- Curseur -->
            <div
              class="absolute w-3 h-3 rounded-full border-2 border-white shadow pointer-events-none"
              :style="{
                left: `${sat}%`,
                top: `${100 - bri}%`,
                transform: 'translate(-50%, -50%)',
                background: currentColor,
                boxShadow: '0 0 0 1px rgba(0,0,0,0.4)',
              }"
            />
          </div>

          <!-- Hue slider -->
          <div
            ref="hueRef"
            class="relative w-full h-3 rounded-full select-none"
            style="background: linear-gradient(to right,#f00,#ff0,#0f0,#0ff,#00f,#f0f,#f00); cursor: pointer"
            @mousedown.prevent="startHue"
          >
            <div
              class="absolute w-3 h-3 rounded-full border-2 border-white pointer-events-none"
              :style="{
                left: `${hue / 360 * 100}%`,
                top: '50%',
                transform: 'translate(-50%, -50%)',
                background: `hsl(${hue},100%,50%)`,
                boxShadow: '0 0 0 1px rgba(0,0,0,0.4)',
              }"
            />
          </div>

          <!-- Hex input + aperçu -->
          <div class="flex items-center gap-2">
            <div class="w-5 h-5 rounded-full ring-1 ring-white/20 shrink-0" :style="{ background: currentColor }" />
            <input
              type="text"
              :value="currentColor"
              maxlength="7"
              class="flex-1 bg-slate-700 text-xs text-slate-200 rounded-lg px-2 py-1 outline-none border border-white/10 focus:border-white/30"
              @mousedown.stop
              @input="onHexInput"
            />
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const PRESETS = [
  '#FFFFFF', '#000000', '#0000FF', '#000080',
  '#FF0000', '#008000', '#A5A5A5', '#FF8C00',
  '#800080', '#FFD700',
]
const MAX_RECENT = 10

const props = defineProps<{ activeColor: string }>()
const emit = defineEmits<{
  applyColor:       [color: string]
  saveSelection:    []
  colorPickerClose: []
}>()

const show         = ref(false)
const pos          = ref({ top: '0px', left: '0px' })
const btnRef       = ref<HTMLElement | null>(null)
const panelRef     = ref<HTMLElement | null>(null)
const currentColor = ref(props.activeColor || '#ffffff')
const recentColors = ref<string[]>([])

// État HSV (sat=0-100, bri=0-100, hue=0-360)
const hue = ref(0)
const sat = ref(100)
const bri = ref(100)

const sbRef  = ref<HTMLElement | null>(null)
const hueRef = ref<HTMLElement | null>(null)

// ── Conversions ──────────────────────────────────────────────────────────────
const hexToHsv = (hex: string): { h: number; s: number; v: number } => {
  const r = parseInt(hex.slice(1,3),16)/255
  const g = parseInt(hex.slice(3,5),16)/255
  const b = parseInt(hex.slice(5,7),16)/255
  const max = Math.max(r,g,b), min = Math.min(r,g,b), d = max - min
  let h = 0
  if (d !== 0) {
    switch(max){
      case r: h = ((g - b) / d % 6) * 60; break
      case g: h = ((b - r) / d + 2)  * 60; break
      case b: h = ((r - g) / d + 4)  * 60; break
    }
    if (h < 0) h += 360
  }
  return {
    h: Math.round(h),
    s: max === 0 ? 0 : Math.round((d / max) * 100),
    v: Math.round(max * 100),
  }
}

const hsvToHex = (h: number, s: number, v: number): string => {
  const S = s / 100, V = v / 100
  const f = (n: number) => {
    const k = (n + h / 60) % 6
    return V - V * S * Math.max(0, Math.min(k, 4 - k, 1))
  }
  const toHex = (x: number) => Math.round(x * 255).toString(16).padStart(2,'0')
  return `#${toHex(f(5))}${toHex(f(3))}${toHex(f(1))}`
}

const syncFromHex = (hex: string) => {
  if (!/^#[0-9a-fA-F]{6}$/.test(hex)) return
  const { h, s, v } = hexToHsv(hex)
  hue.value = h
  sat.value = s
  bri.value = v
}

watch(() => props.activeColor, (v) => {
  if (v) { currentColor.value = v; syncFromHex(v) }
})

// ── Mise à jour couleur depuis HSV ───────────────────────────────────────────
const updateColor = () => {
  const hex = hsvToHex(hue.value, sat.value, bri.value)
  currentColor.value = hex
  emit('applyColor', hex)
}

// ── Helpers : position relative dans un élément ──────────────────────────────
const clamp = (v: number) => Math.max(0, Math.min(1, v))

const relativePos = (e: MouseEvent, el: HTMLElement) => {
  const r = el.getBoundingClientRect()
  return {
    x: clamp((e.clientX - r.left)  / r.width),
    y: clamp((e.clientY - r.top)   / r.height),
  }
}

// ── Drag : SB box ────────────────────────────────────────────────────────────
const moveSB = (e: MouseEvent) => {
  if (!sbRef.value) return
  const { x, y } = relativePos(e, sbRef.value)
  sat.value = Math.round(x * 100)
  bri.value = Math.round((1 - y) * 100)
  updateColor()
}

const startSB = (e: MouseEvent) => {
  moveSB(e)
  const onMove = (ev: MouseEvent) => moveSB(ev)
  const onUp   = () => {
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup',   onUp)
  }
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup',   onUp)
}

// ── Drag : Hue slider ────────────────────────────────────────────────────────
const moveHue = (e: MouseEvent) => {
  if (!hueRef.value) return
  const { x } = relativePos(e, hueRef.value)
  hue.value = Math.round(x * 360)
  updateColor()
}

const startHue = (e: MouseEvent) => {
  moveHue(e)
  const onMove = (ev: MouseEvent) => moveHue(ev)
  const onUp   = () => {
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup',   onUp)
  }
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup',   onUp)
}

// ── Hex input ────────────────────────────────────────────────────────────────
const onHexInput = (e: Event) => {
  const val = (e.target as HTMLInputElement).value
  if (/^#[0-9a-fA-F]{6}$/.test(val)) {
    currentColor.value = val
    syncFromHex(val)
    emit('applyColor', val)
  }
}

// ── Toggle / Apply ───────────────────────────────────────────────────────────
const toggle = () => {
  if (!show.value) {
    emit('saveSelection')
    syncFromHex(currentColor.value)
    if (btnRef.value) {
      const r    = btnRef.value.getBoundingClientRect()
      const left = Math.min(r.left, window.innerWidth - 240)
      pos.value  = { top: `${r.bottom + 4}px`, left: `${left}px` }
    }
  }
  show.value = !show.value
}

const close = () => { show.value = false }

const apply = (color: string) => {
  emit('saveSelection')
  currentColor.value = color
  syncFromHex(color)
  emit('applyColor', color)
  addRecent(color)
  show.value = false
  emit('colorPickerClose')
}

const addRecent = (color: string) => {
  const filtered     = recentColors.value.filter(c => c.toLowerCase() !== color.toLowerCase())
  recentColors.value = [color, ...filtered].slice(0, MAX_RECENT)
}

defineExpose({ panelRef, close })
</script>