<script setup>
import { computed } from 'vue'

const props = defineProps({
  table_type: { type: String, required: true },
  tilt: { type: Number, default: 0 }
})

const style = computed(() => ({ transform: `rotate(${props.tilt}deg)` }))
</script>

<template>
  <svg viewBox="0 0 48 32" fill="currentColor" class="block w-full" :style="style">
    <template v-if="table_type === 'ROUND_2'">
      <circle cx="8" cy="16" r="4.2" opacity="0.55" />
      <circle cx="40" cy="16" r="4.2" opacity="0.55" />
      <circle cx="24" cy="16" r="10.5" />
    </template>
    <template v-else-if="table_type === 'RECT_4'">
      <circle cx="16" cy="5" r="4" opacity="0.55" />
      <circle cx="32" cy="5" r="4" opacity="0.55" />
      <circle cx="16" cy="27" r="4" opacity="0.55" />
      <circle cx="32" cy="27" r="4" opacity="0.55" />
      <rect x="10" y="9" width="28" height="14" rx="6" />
    </template>
    <template v-else>
      <circle cx="12" cy="5.5" r="3.6" opacity="0.55" />
      <circle cx="24" cy="5.5" r="3.6" opacity="0.55" />
      <circle cx="36" cy="5.5" r="3.6" opacity="0.55" />
      <circle cx="12" cy="26.5" r="3.6" opacity="0.55" />
      <circle cx="24" cy="26.5" r="3.6" opacity="0.55" />
      <circle cx="36" cy="26.5" r="3.6" opacity="0.55" />
      <rect x="5" y="10" width="38" height="12" rx="6" />
    </template>
  </svg>
</template>
