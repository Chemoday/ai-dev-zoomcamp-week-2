<script setup>
import { useRestaurant } from '../composables/useRestaurant'
import { format_window, format_day } from '../utils/format'

const emit = defineEmits(['inspect'])
const { tables, day_reservations, filters } = useRestaurant()

function table_for(table_id) {
  return tables.value.find((t) => t.id === table_id) || null
}
</script>

<template>
  <aside class="w-[380px] flex-none">
    <div class="mb-3 flex items-baseline gap-3">
      <h3 class="text-[25px]">Bookings</h3>
      <span class="text-[13px] text-text-secondary">{{ format_day(filters.date) }}</span>
    </div>

    <div class="card shadow-md">
      <table v-if="day_reservations.length" class="w-full border-collapse text-sm">
        <thead>
          <tr>
            <th
              v-for="head in ['Guest', 'Table', 'Time']"
              :key="head"
              class="border-b border-border-default px-2 py-2 text-left text-[11px] uppercase tracking-wider text-text-secondary"
            >
              {{ head }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="reservation in day_reservations"
            :key="reservation.id"
            class="cursor-pointer transition-colors hover:bg-black/5"
            @click="emit('inspect', table_for(reservation.table_id))"
          >
            <td class="border-b border-black/5 px-2 py-2">
              <div>{{ reservation.customer_name }}</div>
              <div class="text-[11px] text-text-secondary">{{ reservation.customer_phone }}</div>
            </td>
            <td class="border-b border-black/5 px-2 py-2">
              Table {{ table_for(reservation.table_id)?.table_number ?? '—' }}
            </td>
            <td class="border-b border-black/5 px-2 py-2">
              {{ format_window(reservation.start_hour, reservation.duration_hours) }}
            </td>
          </tr>
        </tbody>
      </table>

      <p v-else class="py-3 text-[13px] text-text-secondary">No bookings for this date.</p>
    </div>
  </aside>
</template>
