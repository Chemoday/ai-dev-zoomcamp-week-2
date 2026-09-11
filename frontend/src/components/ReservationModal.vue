<script setup>
import { computed, reactive, ref } from 'vue'
import TableShape from './TableShape.vue'
import { useRestaurant } from '../composables/useRestaurant'
import { useToasts } from '../composables/useToasts'
import { HOURS, TYPE_LABEL, format_hour } from '../utils/format'

const props = defineProps({ table: { type: Object, required: true } })
const emit = defineEmits(['close'])

const { filters, book_table } = useRestaurant()
const { push_toast } = useToasts()

const form = reactive({
  customer_name: '',
  customer_phone: '',
  reservation_date: filters.date,
  start_time: filters.start_time,
  duration: filters.duration
})

const status = ref('default') // default | submitting | success
const touched = ref(false)
const conflict_message = ref('')
const shake_key = ref(0)

const errors = computed(() => {
  const result = {}
  if (!form.customer_name.trim()) result.customer_name = 'Please enter a name.'
  const digits = (form.customer_phone.match(/\d/g) || []).length
  if (!form.customer_phone.trim()) result.customer_phone = 'Please enter a phone number.'
  else if (digits < 7) result.customer_phone = 'That phone number looks incomplete.'
  return result
})

const is_valid = computed(() => Object.keys(errors.value).length === 0)

async function submit() {
  if (status.value === 'submitting') return
  if (!is_valid.value) {
    touched.value = true
    shake_key.value += 1
    return
  }
  status.value = 'submitting'
  conflict_message.value = ''
  try {
    await book_table({ table_id: props.table.id, ...form })
    status.value = 'success'
    setTimeout(() => {
      push_toast('Reservation confirmed')
      emit('close')
    }, 700)
  } catch (error) {
    status.value = 'default'
    if (error.status === 409) {
      conflict_message.value = error.message
    } else {
      conflict_message.value = 'Network error — the request did not go through. Try again.'
      push_toast('Network error — could not reach the server', { tone: 'error', sticky: true })
    }
  }
}
</script>

<template>
  <div
    class="fixed inset-0 z-[80] grid place-items-center bg-neutral-900/50 p-4"
    @click.self="emit('close')"
  >
    <div class="flex w-[min(460px,100%)] flex-col gap-3 rounded-card bg-surface-raised p-5 shadow-lg">
      <div v-if="status === 'success'" class="flex flex-col items-center gap-3 py-6">
        <div class="grid h-16 w-16 animate-check-pop place-items-center rounded-full bg-available">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#f5ead8" stroke-width="2.75" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 6 9 17l-5-5" />
          </svg>
        </div>
        <p class="font-display text-xl">Reservation confirmed</p>
      </div>

      <template v-else>
        <div class="flex items-center gap-4">
          <div class="w-20 flex-none text-available">
            <TableShape :table_type="table.table_type" />
          </div>
          <div>
            <p class="font-display text-xl">Reserve table {{ table.table_number }}</p>
            <p class="text-[13px] text-text-secondary">
              {{ TYPE_LABEL[table.table_type] }} table · seats {{ table.capacity }} · {{ table.table_type }}
            </p>
          </div>
        </div>

        <p v-if="conflict_message" class="rounded-2xl bg-accent-tint-strong px-3 py-2 text-[13px] text-warning-text">
          {{ conflict_message }}
        </p>

        <label :key="`name-${shake_key}`" :class="touched && errors.customer_name ? 'animate-shake' : ''">
          <span class="field-label">Name</span>
          <input
            v-model="form.customer_name"
            class="input"
            :class="touched && errors.customer_name ? 'input-invalid' : ''"
            placeholder="Your name"
          />
          <span v-if="touched && errors.customer_name" class="mt-1 block text-[11px] text-accent-press">
            {{ errors.customer_name }}
          </span>
        </label>

        <label :key="`phone-${shake_key}`" :class="touched && errors.customer_phone ? 'animate-shake' : ''">
          <span class="field-label">Phone</span>
          <input
            v-model="form.customer_phone"
            class="input"
            :class="touched && errors.customer_phone ? 'input-invalid' : ''"
            placeholder="(555) 012 3456"
          />
          <span v-if="touched && errors.customer_phone" class="mt-1 block text-[11px] text-accent-press">
            {{ errors.customer_phone }}
          </span>
        </label>

        <div class="flex gap-3">
          <label class="flex-1">
            <span class="field-label">Date</span>
            <input v-model="form.reservation_date" type="date" class="input" />
          </label>
          <label class="flex-1">
            <span class="field-label">Time</span>
            <select v-model.number="form.start_time" class="input">
              <option v-for="hour in HOURS" :key="hour" :value="hour">{{ format_hour(hour) }}</option>
            </select>
          </label>
          <label class="flex-1">
            <span class="field-label">Duration</span>
            <select v-model.number="form.duration" class="input">
              <option :value="1">1 hour</option>
              <option :value="2">2 hours</option>
              <option :value="3">3 hours</option>
            </select>
          </label>
        </div>

        <div class="mt-2 flex justify-end gap-2">
          <button type="button" class="btn btn-secondary" @click="emit('close')">Cancel</button>
          <button
            type="button"
            class="btn btn-primary min-w-[150px]"
            :disabled="status === 'submitting' || !is_valid"
            @click="submit"
          >
            {{ status === 'submitting' ? 'Booking…' : 'Confirm reservation' }}
          </button>
        </div>
      </template>
    </div>
  </div>
</template>
