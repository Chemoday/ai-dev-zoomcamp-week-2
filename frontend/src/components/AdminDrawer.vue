<script setup>
import { computed, ref, watch } from 'vue'
import TableShape from './TableShape.vue'
import { useRestaurant } from '../composables/useRestaurant'
import { useToasts } from '../composables/useToasts'
import { TYPE_LABEL, format_window, format_day, tilt_for } from '../utils/format'
import { today_iso } from '../services/api'

const props = defineProps({ table: { type: Object, required: true } })
const emit = defineEmits(['close'])

const { future_bookings, remove_table } = useRestaurant()
const { push_toast } = useToasts()

const delete_state = ref('idle') // idle | confirm | deleting

watch(() => props.table.id, () => {
  delete_state.value = 'idle'
})

const bookings = computed(() => future_bookings(props.table.id))
const delete_blocked = computed(() => bookings.value.length > 0)

async function confirm_delete() {
  delete_state.value = 'deleting'
  try {
    await remove_table(props.table.id)
    emit('close')
    push_toast('Table deleted')
  } catch (error) {
    delete_state.value = 'idle'
    push_toast(error.message || 'Network error — could not reach the server', {
      tone: 'error',
      sticky: error.status === 0
    })
  }
}
</script>

<template>
  <aside
    class="fixed inset-y-0 right-0 z-[70] flex w-[400px] flex-col gap-4 overflow-auto
           rounded-l-card bg-surface-raised p-6 shadow-xl"
  >
    <div class="flex items-start gap-3">
      <div class="w-16 flex-none text-available-hover">
        <TableShape :table_type="table.table_type" :tilt="tilt_for(table.id)" />
      </div>
      <div class="flex-1">
        <h3 class="mb-1 text-[25px]">Table {{ table.table_number }}</h3>
        <p class="text-[13px] text-text-secondary">
          {{ TYPE_LABEL[table.table_type] }} · seats {{ table.capacity }} · {{ table.table_type }}
        </p>
      </div>
      <button type="button" class="btn btn-secondary btn-icon" aria-label="Close" @click="emit('close')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.75" stroke-linecap="round">
          <path d="M18 6 6 18M6 6l12 12" />
        </svg>
      </button>
    </div>

    <div>
      <h6 class="mb-2 text-[13px] uppercase tracking-widest text-text-secondary">Bookings</h6>
      <div v-if="bookings.length" class="flex flex-col gap-2">
        <div
          v-for="booking in bookings"
          :key="booking.id"
          class="flex justify-between gap-3 rounded-2xl bg-surface p-3"
        >
          <div>
            <p class="text-sm">{{ booking.customer_name }}</p>
            <p class="text-[11px] text-text-secondary">{{ booking.customer_phone }}</p>
          </div>
          <div class="text-right text-xs">
            <p>{{ booking.reservation_date === today_iso() ? 'Today' : format_day(booking.reservation_date) }}</p>
            <p class="text-text-secondary">{{ format_window(booking.start_time, booking.duration) }}</p>
          </div>
        </div>
      </div>
      <p v-else class="text-[13px] text-text-secondary">No active bookings.</p>
    </div>

    <div class="mt-auto flex flex-col gap-2">
      <p v-if="delete_blocked" class="rounded-2xl bg-accent-tint px-3 py-2 text-xs text-warning-text">
        Cannot delete — has active bookings
      </p>

      <button
        v-if="delete_state === 'idle'"
        type="button"
        class="btn btn-secondary btn-block border-accent/40 text-accent-press"
        :disabled="delete_blocked"
        @click="delete_state = 'confirm'"
      >
        Delete table
      </button>

      <div v-else class="flex items-center gap-2 rounded-2xl bg-surface p-3">
        <span class="flex-1 text-[13px]">Are you sure?</span>
        <button type="button" class="btn btn-secondary text-[13px]" @click="delete_state = 'idle'">Cancel</button>
        <button type="button" class="btn btn-primary text-[13px]" :disabled="delete_state === 'deleting'" @click="confirm_delete">
          {{ delete_state === 'deleting' ? 'Deleting…' : 'Confirm delete' }}
        </button>
      </div>
    </div>
  </aside>
</template>
