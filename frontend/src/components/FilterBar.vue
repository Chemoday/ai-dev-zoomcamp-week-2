<script setup>
import { computed } from 'vue'
import { useRestaurant } from '../composables/useRestaurant'
import { HOURS, format_hour } from '../utils/format'

const { role, filters, refresh_availability } = useRestaurant()

const party_sizes = [1, 2, 3, 4, 5, 6, 7, 8]

const legend = computed(() =>
  role.value === 'guest'
    ? [
        { label: 'Available', class: 'bg-available' },
        { label: 'Too small', class: 'bg-too-small' },
        { label: 'Reserved', class: 'bg-reserved' }
      ]
    : [
        { label: 'Table', class: 'bg-surface-raised border border-border-default' },
        { label: 'Empty slot', class: 'bg-too-small' }
      ]
)
</script>

<template>
  <section class="mx-6 mb-4 flex flex-wrap items-end gap-6 rounded-card bg-surface-raised px-6 py-4">
    <label class="min-w-[160px]">
      <span class="field-label">Date</span>
      <input v-model="filters.date" type="date" class="input" @change="refresh_availability" />
    </label>

    <label class="min-w-[130px]">
      <span class="field-label">Time</span>
      <select v-model.number="filters.start_time" class="input" @change="refresh_availability">
        <option v-for="hour in HOURS" :key="hour" :value="hour">{{ format_hour(hour) }}</option>
      </select>
    </label>

    <label class="min-w-[120px]">
      <span class="field-label">Duration</span>
      <select v-model.number="filters.duration" class="input" @change="refresh_availability">
        <option :value="1">1 hour</option>
        <option :value="2">2 hours</option>
        <option :value="3">3 hours</option>
      </select>
    </label>

    <label class="min-w-[120px]">
      <span class="field-label">Party size</span>
      <select v-model.number="filters.party_size" class="input" @change="refresh_availability">
        <option v-for="size in party_sizes" :key="size" :value="size">
          {{ size }} {{ size === 1 ? 'guest' : 'guests' }}
        </option>
      </select>
    </label>

    <div class="ml-auto flex items-center gap-4 text-xs">
      <span v-for="item in legend" :key="item.label" class="inline-flex items-center gap-2">
        <i class="block h-3.5 w-3.5 rounded-full" :class="item.class" />
        {{ item.label }}
      </span>
    </div>
  </section>
</template>
