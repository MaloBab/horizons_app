import { ref, onBeforeUnmount } from 'vue'

type ToastType = 'success' | 'error' | 'warning' | 'info'

export function useToast(duration = 5000) {
  const toast = ref<{ show: boolean; message: string; type: ToastType }>({
    show: false, message: '', type: 'success',
  })

  let timer: ReturnType<typeof setTimeout> | null = null

  const showToast = (message: string, type: ToastType = 'success') => {
    if (timer) clearTimeout(timer)
    toast.value = { show: true, message, type }
    timer = setTimeout(() => { toast.value.show = false }, duration)
  }

  const hideToast = () => {
    if (timer) clearTimeout(timer)
    toast.value.show = false
  }

  onBeforeUnmount(() => { if (timer) clearTimeout(timer) })

  return { toast, showToast, hideToast }
}