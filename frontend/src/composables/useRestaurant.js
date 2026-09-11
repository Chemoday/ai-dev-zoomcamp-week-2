import { reactive, ref, computed } from 'vue'
import * as api from '../services/api'
import { useToasts } from './useToasts'

const { push_toast } = useToasts()

const role = ref('guest')
const banner_seen = ref(false)
const banner_open = ref(false)

const tables = ref([])
const reservations = ref([])
const availability = ref([])

const loading = ref(true)
const refreshing = ref(false)
const load_error = ref(false)

const popped_ids = ref([])
const deleting_ids = ref([])

const filters = reactive({
  date: api.today_iso(),
  start_time: 19,
  duration: 2,
  party_size: 2
})

const availability_by_table = computed(() => {
  const map = {}
  availability.value.forEach((entry) => {
    map[entry.table_id] = entry
  })
  return map
})

const day_reservations = computed(() =>
  reservations.value.filter((r) => r.reservation_date === filters.date)
)

const any_available = computed(() =>
  availability.value.some((entry) => entry.is_available)
)

async function load_floor() {
  loading.value = true
  load_error.value = false
  try {
    const [table_rows, availability_rows, reservation_rows] = await Promise.all([
      api.fetch_tables(),
      api.fetch_availability(filters),
      api.fetch_reservations(filters.date)
    ])
    tables.value = table_rows
    availability.value = availability_rows
    reservations.value = reservation_rows
  } catch (error) {
    load_error.value = true
  } finally {
    loading.value = false
  }
}

async function refresh_availability() {
  refreshing.value = true
  try {
    const [availability_rows, reservation_rows] = await Promise.all([
      api.fetch_availability(filters),
      api.fetch_reservations(filters.date)
    ])
    availability.value = availability_rows
    reservations.value = reservation_rows
  } catch (error) {
    push_toast('Network error — could not reach the server', { tone: 'error', sticky: true })
  } finally {
    refreshing.value = false
  }
}

function set_role(next_role) {
  if (next_role === 'staff' && !banner_seen.value) {
    banner_seen.value = true
    banner_open.value = true
  }
  role.value = next_role
}

function future_bookings(table_id) {
  const today = api.today_iso()
  return reservations.value.filter(
    (r) => r.table_id === table_id && r.reservation_date >= today
  )
}

async function book_table(payload) {
  const reservation = await api.create_reservation(payload)
  await refresh_availability()
  return reservation
}

async function add_table(payload) {
  const table = await api.create_table(payload)
  tables.value.push(table)
  popped_ids.value.push(table.id)
  setTimeout(() => {
    popped_ids.value = popped_ids.value.filter((id) => id !== table.id)
  }, 400)
  await refresh_availability()
  return table
}

async function remove_table(table_id) {
  await api.delete_table(table_id)
  deleting_ids.value.push(table_id)
  setTimeout(() => {
    tables.value = tables.value.filter((t) => t.id !== table_id)
    deleting_ids.value = deleting_ids.value.filter((id) => id !== table_id)
  }, 220)
}

export function useRestaurant() {
  return {
    role,
    banner_open,
    tables,
    reservations,
    availability_by_table,
    day_reservations,
    any_available,
    loading,
    refreshing,
    load_error,
    popped_ids,
    deleting_ids,
    filters,
    load_floor,
    refresh_availability,
    set_role,
    future_bookings,
    book_table,
    add_table,
    remove_table
  }
}
