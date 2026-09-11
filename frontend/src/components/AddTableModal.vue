<script setup>
import { computed, reactive, ref, watch } from 'vue'
import TableShape from './TableShape.vue'
import { useRestaurant } from '../composables/useRestaurant'
import { useToasts } from '../composables/useToasts'
import { TYPE_NOTE } from '../utils/format'
import { TYPE_CAPACITY } from '../api/mock_api'

const props = defineProps({ slot_position: { type: Object, required: true } })
const emit = defineEmits(['close'])

const { tables, add_table } = useRestaurant()
const { push_toast } = useToasts()

const form = reactive({ table_number: '', table_type: 'ROUND_2', capacity: 2 })
const status = ref('default')
const touched = ref(false)
const conflict_message = ref('')
const shake_key = ref(0)

watch(
  () => form.table_type,
  (table_type) => {
    form.capacity = TYPE_CAPACITY[table_type]
  }
)

const parsed_number = computed(() => parseInt(form.table_number, 10) || 0)
const is_duplicate = computed(
  () => parsed_number.value > 0 && tables.value.some((t) => t.table_number === parsed_number.value)
)
const number_error = computed(() => {
  if (!touched.value) return ''
  if (!parsed_number.value) return 'Enter a table number.'
  if (is_duplicate.value) return 'That table number already exists.'
  return ''
})

async function submit() {
  if (status.value === 'submitting') return
  if (!parsed_number.value || is_duplicate.value) {
    touched.value = true
    shake_key.value += 1
    return
  }
  status.value = 'submitting'
  conflict_message.value = ''
  try {
    await add_table({
      table_number: parsed_number.value,
      capacity: parseInt(form.capacity, 10) || TYPE_CAPACITY[form.table_type],
      table_type: form.table_type,
      pos_x: props.slot_position.pos_x,
      pos_y: props.slot_position.pos_y
    })
    push_toast('Table added')
    emit('close')
  } catch (error) {
    status.value = 'default'
    if (error.status === 409) {
      conflict_message.value = 'Another staff member just placed a table here.'
    } else {
      conflict_message.value = 'Network error — the table was not created.'
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
    <div class="flex w-[min(440px,100%)] flex-col gap-3 rounded-card bg-surface-raised p-5 shadow-lg">
      <div>
        <p class="font-display text-xl">Add a table</p>
        <p class="text-[13px] text-text-secondary">
          Position row {{ slot_position.pos_y + 1 }}, column {{ slot_position.pos_x + 1 }}
        </p>
      </div>

      <p v-if="conflict_message" class="rounded-2xl bg-accent-tint-strong px-3 py-2 text-[13px] text-warning-text">
        {{ conflict_message }}
      </p>

      <div class="flex items-center gap-4 rounded-cell bg-surface px-4 py-3">
        <div class="w-24 flex-none text-available-hover">
          <TableShape :table_type="form.table_type" />
        </div>
        <p class="text-[13px] text-text-secondary">{{ TYPE_NOTE[form.table_type] }}</p>
      </div>

      <label :key="`number-${shake_key}`" :class="number_error ? 'animate-shake' : ''">
        <span class="field-label">Table number</span>
        <input
          v-model="form.table_number"
          class="input"
          :class="number_error ? 'input-invalid' : ''"
          placeholder="e.g. 14"
        />
        <span v-if="number_error" class="mt-1 block text-[11px] text-accent-press">{{ number_error }}</span>
      </label>

      <label>
        <span class="field-label">Type</span>
        <select v-model="form.table_type" class="input">
          <option value="ROUND_2">ROUND_2 — round, seats 2</option>
          <option value="RECT_4">RECT_4 — rectangular, seats 4</option>
          <option value="LONG_6">LONG_6 — long, seats 6</option>
        </select>
      </label>

      <label>
        <span class="field-label">Capacity</span>
        <input v-model.number="form.capacity" type="number" min="1" class="input" />
      </label>

      <div class="mt-2 flex justify-end gap-2">
        <button type="button" class="btn btn-secondary" @click="emit('close')">Cancel</button>
        <button type="button" class="btn btn-primary min-w-[130px]" :disabled="status === 'submitting'" @click="submit">
          {{ status === 'submitting' ? 'Adding…' : 'Add table' }}
        </button>
      </div>
    </div>
  </div>
</template>
