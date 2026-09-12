import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import App from '../src/App.vue'
import * as api from '../src/services/api'

const TABLE = { id: 1, table_number: 1, capacity: 2, table_type: 'ROUND_2', grid_x: 0, grid_y: 0 }

vi.mock('../src/services/api', () => ({
  USE_MOCKS: true,
  today_iso: () => '2024-01-01',
  TYPE_CAPACITY: { ROUND_2: 2, RECT_4: 4, LONG_6: 6 },
  demo_flags: { force_conflict: false, force_network: false },
  fetch_tables: vi.fn(),
  fetch_availability: vi.fn(),
  fetch_reservations: vi.fn(),
  create_reservation: vi.fn(),
  create_table: vi.fn(),
  delete_table: vi.fn(),
  reset_data: vi.fn(),
  clear_floor: vi.fn()
}))

function find_button(wrapper, text) {
  return wrapper.findAll('button').find((b) => b.text().includes(text))
}

describe('guest booking flow (smoke test)', () => {
  it('lets a guest see an available table, book it, and see it turn reserved', async () => {
    api.fetch_tables.mockResolvedValue([TABLE])
    api.fetch_availability.mockResolvedValue([
      { table_id: 1, is_reserved: false, fits_party: true, is_available: true }
    ])
    api.fetch_reservations.mockResolvedValue([])
    api.create_reservation.mockImplementation(async (payload) => ({
      id: 100,
      ...payload,
      end_time: payload.start_time + payload.duration
    }))

    const wrapper = mount(App)
    await flushPromises()

    // The one seeded table renders as an available, clickable cell.
    const table_button = find_button(wrapper, 'Seats 2')
    expect(table_button).toBeTruthy()
    expect(table_button.attributes('disabled')).toBeUndefined()

    // Clicking it opens the reservation modal.
    await table_button.trigger('click')
    await flushPromises()
    expect(wrapper.text()).toContain('Reserve table 1')

    // Fill in the guest's details.
    await wrapper.find('input[placeholder="Your name"]').setValue('Ada Lovelace')
    await wrapper.find('input[placeholder="(555) 012 3456"]').setValue('555-123-4567')

    // Once availability reflects the new booking, the mock should
    // report the table as reserved on the next refresh.
    api.fetch_availability.mockResolvedValue([
      { table_id: 1, is_reserved: true, fits_party: true, is_available: false }
    ])

    await find_button(wrapper, 'Confirm reservation').trigger('click')
    await flushPromises()

    expect(api.create_reservation).toHaveBeenCalledWith(
      expect.objectContaining({
        table_id: 1,
        customer_name: 'Ada Lovelace',
        customer_phone: '555-123-4567'
      })
    )
    expect(wrapper.text()).toContain('Reservation confirmed')

    // The modal auto-closes ~700ms after success.
    await new Promise((resolve) => setTimeout(resolve, 800))
    await flushPromises()

    expect(wrapper.text()).not.toContain('Reserve table 1')
    // The floor grid re-fetched availability and now shows the table as reserved.
    expect(find_button(wrapper, 'Reserved')).toBeTruthy()
  })
})
