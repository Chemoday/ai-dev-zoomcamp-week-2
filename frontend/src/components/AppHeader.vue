<script setup>
import { useRestaurant } from '../composables/useRestaurant'
import { USE_MOCKS } from '../services/api'

defineProps({ demo_open: { type: Boolean, default: false } })
defineEmits(['toggle-demo'])

const { role, set_role } = useRestaurant()
</script>

<template>
  <header class="flex items-center gap-4 px-6 py-4">
    <div class="mr-auto font-display text-[22px]">
      Fern &amp; Field
      <span class="font-body text-[13px] tracking-wide text-text-secondary">· table reservations</span>
    </div>

    <div class="inline-flex overflow-hidden rounded-field border border-border-default bg-surface-raised">
      <button
        v-for="option in ['guest', 'staff']"
        :key="option"
        type="button"
        class="px-3.5 py-1.5 text-[13px] capitalize transition-colors"
        :class="role === option ? 'bg-accent text-surface' : 'hover:bg-black/5'"
        @click="set_role(option)"
      >
        {{ option }}
      </button>
    </div>

    <button
      v-if="USE_MOCKS"
      type="button"
      class="btn btn-secondary text-[13px]"
      @click="$emit('toggle-demo')"
    >
      Demo states
    </button>
  </header>
</template>
