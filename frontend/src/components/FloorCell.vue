<script setup>
import { computed } from 'vue'
import TableShape from './TableShape.vue'
import { TYPE_LABEL, tilt_for } from '../utils/format'

const props = defineProps({
  table: { type: Object, default: null },
  mode: { type: String, required: true },
  state: { type: String, required: true }, // empty | available | too_small | reserved | staff
  loading: { type: Boolean, default: false },
  popped: { type: Boolean, default: false },
  deleting: { type: Boolean, default: false }
})

const emit = defineEmits(['select'])

const interactive = computed(
  () => !props.loading && !props.deleting && (props.state === 'available' || props.mode === 'staff')
)

const tone = computed(() => {
  if (props.loading) {
    return props.mode === 'staff'
      ? 'border border-dashed border-neutral-300 animate-pulse-cell'
      : 'bg-too-small animate-pulse-cell'
  }
  if (props.deleting) return 'bg-too-small opacity-0 scale-50'
  if (!props.table) {
    return props.mode === 'staff'
      ? 'border-[1.5px] border-dashed border-neutral-400 text-neutral-600'
      : 'border border-dashed border-black/5'
  }
  if (props.mode === 'staff') return 'bg-surface-raised border border-border-default'
  if (props.state === 'reserved') return 'bg-reserved text-[#fff6ee]'
  if (props.state === 'too_small') return 'bg-too-small text-neutral-800'
  return 'bg-available text-[#f7fbef] hover:bg-available-hover'
})

const badge = computed(() => {
  if (!props.table || props.loading || props.deleting) return null
  if (props.mode === 'staff') {
    return props.state === 'reserved'
      ? { text: 'Booked', class: 'bg-accent-tint-strong text-warning-text' }
      : null
  }
  if (props.state === 'reserved') return { text: 'Reserved', class: 'bg-white/20 text-[#fff6ee]' }
  if (props.state === 'too_small') return { text: 'Too small', class: 'bg-neutral-200 text-neutral-800' }
  return null
})
</script>

<template>
  <button
    type="button"
    :disabled="!interactive"
    class="flex aspect-square flex-col items-center justify-center gap-1 rounded-cell p-1.5
           transition-[transform,box-shadow,background-color,opacity] duration-200"
    :class="[
      tone,
      interactive ? 'cursor-pointer hover:-translate-y-0.5 hover:shadow-lg' : 'cursor-default',
      popped ? 'animate-pop-in' : ''
    ]"
    @click="interactive && emit('select')"
  >
    <template v-if="!loading && !deleting">
      <div v-if="table" class="w-[68%]">
        <TableShape :table_type="table.table_type" :tilt="tilt_for(table.id)" />
      </div>
      <span v-if="table" class="font-display text-[15px] leading-none">{{ table.table_number }}</span>
      <span v-else-if="mode === 'staff'" class="font-display text-[19px] leading-none">+</span>

      <span v-if="table" class="text-[11px] opacity-85">
        {{ mode === 'staff' ? `${TYPE_LABEL[table.table_type]} · ${table.capacity}` : `Seats ${table.capacity}` }}
      </span>

      <span v-if="badge" class="tag" :class="badge.class">{{ badge.text }}</span>
    </template>
  </button>
</template>
