<script setup>
import { computed } from 'vue'
import FloorCell from './FloorCell.vue'
import { useRestaurant } from '../composables/useRestaurant'

const emit = defineEmits(['book', 'add', 'inspect'])

const {
  role,
  tables,
  availability_by_table,
  loading,
  refreshing,
  popped_ids,
  deleting_ids
} = useRestaurant()

const GRID_SIZE = 6

const cells = computed(() => {
  const by_coord = {}
  tables.value.forEach((table) => {
    by_coord[`${table.grid_x},${table.grid_y}`] = table
  })

  const list = []
  for (let grid_y = 0; grid_y < GRID_SIZE; grid_y += 1) {
    for (let grid_x = 0; grid_x < GRID_SIZE; grid_x += 1) {
      const table = by_coord[`${grid_x},${grid_y}`] || null
      const entry = table ? availability_by_table.value[table.id] : null
      let state = 'empty'
      if (table) {
        if (role.value === 'staff') state = entry?.is_reserved ? 'reserved' : 'staff'
        else if (entry?.is_reserved) state = 'reserved'
        else if (entry && !entry.fits_party) state = 'too_small'
        else state = 'available'
      }
      list.push({ key: `${grid_x},${grid_y}`, grid_x, grid_y, table, state })
    }
  }
  return list
})

function on_select(cell) {
  if (!cell.table) emit('add', { grid_x: cell.grid_x, grid_y: cell.grid_y })
  else if (role.value === 'staff') emit('inspect', cell.table)
  else emit('book', cell.table)
}
</script>

<template>
  <div class="grid grid-cols-6 gap-3 transition-opacity duration-200" :class="refreshing ? 'opacity-60' : 'opacity-100'">
    <FloorCell
      v-for="cell in cells"
      :key="cell.key"
      :table="cell.table"
      :mode="role"
      :state="cell.state"
      :loading="loading"
      :popped="cell.table ? popped_ids.includes(cell.table.id) : false"
      :deleting="cell.table ? deleting_ids.includes(cell.table.id) : false"
      @select="on_select(cell)"
    />
  </div>
</template>
