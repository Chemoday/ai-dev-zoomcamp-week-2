<script setup>
import { useToasts } from '../composables/useToasts'

const { toasts, dismiss_toast } = useToasts()
</script>

<template>
  <div class="pointer-events-none fixed right-4 top-4 z-[90] flex w-80 flex-col gap-2">
    <TransitionGroup
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="translate-x-6 opacity-0"
      leave-active-class="transition duration-200 ease-in"
      leave-to-class="translate-x-6 opacity-0"
    >
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="pointer-events-auto flex items-center gap-3 rounded-field px-4 py-3 text-[13px] text-[#f7f0e4] shadow-md"
        :class="toast.tone === 'error' ? 'bg-accent-press' : 'bg-neutral-900'"
      >
        <span class="flex-1">{{ toast.text }}</span>
        <button type="button" class="btn btn-ghost text-xs text-inherit" @click="dismiss_toast(toast.id)">
          {{ toast.sticky ? 'Dismiss' : 'Close' }}
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>
