import { type Directive } from 'vue'

interface ClickOutsideElement extends HTMLElement {
  clickOutsideEvent?: (event: Event) => void
}

export const vClickOutside: Directive = {
  mounted(el: ClickOutsideElement, binding) {
    el.clickOutsideEvent = (event: Event) => {
      if (!(el === event.target || el.contains(event.target as Node))) {
        binding.value()
      }
    }
    document.addEventListener('mousedown', el.clickOutsideEvent, true)
  },
  unmounted(el: ClickOutsideElement) {
    if (el.clickOutsideEvent) {
      document.removeEventListener('mousedown', el.clickOutsideEvent, true)
    }
  }
}