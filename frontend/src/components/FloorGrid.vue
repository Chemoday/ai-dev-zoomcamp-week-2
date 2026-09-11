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
    by_coord[`${table.pos_x},${table.pos_y}`] = table
  })

  const list = []
  for (let pos_y = 0; pos_y < GRID_SIZE; pos_y += 1) {
    for (let pos_x = 0; pos_x < GRID_SIZE; pos_x += 1) {
      const table = by_coord[`${pos_x},${pos_y}`] || null
      const entry = table ? availability_by_table.value[table.id] : null
      let state = 'empty'
      if (table) {
        if (role.value === 'staff') state = entry?.is_reserved ? 'reserved' : 'staff'
        else if (entry?.is_reserved) state = 'reserved'
        else if (entry && !entry.fits_party) state = 'too_small'
        else state = 'available'
      }
      list.push({ key: `${pos_x},${pos_y}`, pos_x, pos_y, table, state })
    }
  }
  return list
})

function on_select(cell) {
  if (!cell.table) emit('add', { pos_x: cell.pos_x, pos_y: cell.pos_y })
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
