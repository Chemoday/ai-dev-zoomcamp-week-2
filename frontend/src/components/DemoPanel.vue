<script setup>
import { demo_flags, reset_data, clear_floor } from '../services/api'
import { useRestaurant } from '../composables/useRestaurant'

const emit = defineEmits(['close'])
const { load_floor } = useRestaurant()

function on_clear() {
  clear_floor()
  load_floor()
  emit('close')
}

function on_reset() {
  reset_data()
  load_floor()
  emit('close')
}
</script>

<template>
  <div class="absolute right-6 top-[70px] z-[60] flex w-72 flex-col gap-3 rounded-card bg-surface-raised p-4 shadow-md">
    <p class="text-[10px] uppercase tracking-widest text-accent-press">Prototype controls</p>

    <label class="flex items-center gap-2 text-sm">
      <input v-model="demo_flags.force_conflict" type="checkbox" class="accent-accent" />
      Next submit returns 409
    </label>
    <label class="flex items-center gap-2 text-sm">
      <input v-model="demo_flags.force_network" type="checkbox" class="accent-accent" />
      Next request fails
    </label>

    <div class="flex flex-wrap gap-2">
      <button type="button" class="btn btn-secondary text-xs" @click="on_clear">Empty floor</button>
      <button type="button" class="btn btn-secondary text-xs" @click="on_reset">Reset data</button>
    </div>
  </div>
</template>
