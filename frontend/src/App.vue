<script setup>
import { computed, onMounted, ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import FilterBar from './components/FilterBar.vue'
import FloorGrid from './components/FloorGrid.vue'
import ReservationsList from './components/ReservationsList.vue'
import ReservationModal from './components/ReservationModal.vue'
import AddTableModal from './components/AddTableModal.vue'
import AdminDrawer from './components/AdminDrawer.vue'
import ToastStack from './components/ToastStack.vue'
import DemoPanel from './components/DemoPanel.vue'
import { useRestaurant } from './composables/useRestaurant'
import { format_window, format_day } from './utils/format'
import { USE_MOCKS, API_ORIGIN } from './services/api'

const {
  role,
  banner_open,
  tables,
  day_reservations,
  any_available,
  loading,
  load_error,
  filters,
  load_floor
} = useRestaurant()

const demo_open = ref(false)
const booking_table = ref(null)
const add_slot = ref(null)
const inspected_table = ref(null)

onMounted(load_floor)

const is_guest = computed(() => role.value === 'guest')

const floor_title = computed(() => (is_guest.value ? 'Pick a table' : 'Floor plan'))
const floor_subtitle = computed(() =>
  is_guest.value
    ? `${format_window(filters.start_time, filters.duration)}, party of ${filters.party_size}`
    : `${tables.value.length} tables placed · ${day_reservations.value.length} bookings on ${format_day(filters.date)}`
)

const show_fully_booked = computed(
  () => is_guest.value && !loading.value && tables.value.length > 0 && !any_available.value
)
const show_empty_guest = computed(() => is_guest.value && !loading.value && tables.value.length === 0)
const show_empty_staff = computed(() => !is_guest.value && !loading.value && tables.value.length === 0)

function open_drawer(table) {
  if (table) inspected_table.value = table
}
</script>

<template>
  <div class="relative flex min-h-screen flex-col">
    <AppHeader :demo_open="demo_open" @toggle-demo="demo_open = !demo_open" />
    <DemoPanel v-if="demo_open && USE_MOCKS" @close="demo_open = false" />

    <div
      v-if="banner_open && role === 'staff'"
      class="mx-6 mb-3 flex items-center gap-3 rounded-card bg-warning-surface px-4 py-3 text-[13px] text-warning-text"
    >
      <span class="flex-1">Demo mode: switched to Staff view without full authentication.</span>
      <button type="button" class="btn btn-ghost text-xs text-warning-text" @click="banner_open = false">
        Dismiss
      </button>
    </div>

    <div
      v-if="load_error"
      class="mx-6 mb-3 flex items-center gap-3 rounded-card bg-accent-tint-strong px-4 py-3 text-[13px] text-warning-text"
    >
      <span class="flex-1">
        Could not reach the server. On the free hosting tier the
        backend sleeps after inactivity and can take up to a minute to
        wake up —
        <a :href="`${API_ORIGIN}/docs`" target="_blank" rel="noopener" class="underline">
          open the backend
        </a>
        to wake it, then retry.
      </span>
      <button type="button" class="btn btn-primary text-xs" @click="load_floor">Retry</button>
    </div>

    <FilterBar />

    <main class="flex flex-1 items-start gap-6 px-6 pb-10">
      <section class="min-w-0 max-w-[860px] flex-1">
        <div class="mb-3 flex items-baseline gap-3">
          <h3 class="text-[25px]">{{ floor_title }}</h3>
          <span class="text-[13px] text-text-secondary">{{ floor_subtitle }}</span>
        </div>

        <p v-if="show_fully_booked" class="mb-3 rounded-card bg-neutral-200 px-4 py-3 text-[13px]">
          No tables available for this time — try a different time or party size.
        </p>
        <p v-if="show_empty_guest" class="mb-3 rounded-card bg-neutral-200 px-4 py-3 text-[13px]">
          No tables have been set up yet — check back soon.
        </p>
        <p v-if="show_empty_staff" class="mb-3 rounded-card bg-sage-100 px-4 py-3 text-[13px] text-sage-800">
          The floor is empty. Click any dashed cell to place your first table.
        </p>

        <FloorGrid
          @book="booking_table = $event"
          @add="add_slot = $event"
          @inspect="open_drawer"
        />
      </section>

      <ReservationsList v-if="role === 'staff'" @inspect="open_drawer" />
    </main>

    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      leave-active-class="transition duration-150 ease-in"
      leave-to-class="opacity-0"
    >
      <ReservationModal v-if="booking_table" :table="booking_table" @close="booking_table = null" />
    </Transition>

    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      leave-active-class="transition duration-150 ease-in"
      leave-to-class="opacity-0"
    >
      <AddTableModal v-if="add_slot" :slot_position="add_slot" @close="add_slot = null" />
    </Transition>

    <Transition
      enter-active-class="transition duration-250 ease-out"
      enter-from-class="translate-x-full"
      leave-active-class="transition duration-200 ease-in"
      leave-to-class="translate-x-full"
    >
      <AdminDrawer v-if="inspected_table" :table="inspected_table" @close="inspected_table = null" />
    </Transition>

    <ToastStack />
  </div>
</template>
