import { ref } from 'vue'

const toasts = ref([])
let next_id = 1

export function useToasts() {
  function dismiss_toast(id) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  function push_toast(text, { tone = 'default', sticky = false } = {}) {
    const id = next_id++
    toasts.value.push({ id, text, tone, sticky })
    if (!sticky) setTimeout(() => dismiss_toast(id), 3000)
    return id
  }

  return { toasts, push_toast, dismiss_toast }
}
