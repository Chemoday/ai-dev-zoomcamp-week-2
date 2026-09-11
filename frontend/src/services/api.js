/**
 * Mock API — mirrors the endpoints in product-spec.md §4.
 * Shapes are snake_case, hours are integers, dates are ISO (YYYY-MM-DD).
 * Every call resolves after ~200ms; failures reject with { status, message }.
 */

const LATENCY = 200

export const today_iso = () => new Date().toISOString().slice(0, 10)

export const TYPE_CAPACITY = { ROUND_2: 2, RECT_4: 4, LONG_6: 6 }

/** Demo switches the UI can flip to exercise error paths. */
export const demo_flags = { force_conflict: false, force_network: false }

let db = null

function seed() {
  const date = today_iso()
  db = {
    tables: [
      { id: 1, table_number: 1, capacity: 2, table_type: 'ROUND_2', grid_x: 0, grid_y: 0 },
      { id: 2, table_number: 2, capacity: 2, table_type: 'ROUND_2', grid_x: 2, grid_y: 0 },
      { id: 3, table_number: 3, capacity: 4, table_type: 'RECT_4', grid_x: 4, grid_y: 0 },
      { id: 4, table_number: 4, capacity: 4, table_type: 'RECT_4', grid_x: 1, grid_y: 2 },
      { id: 5, table_number: 5, capacity: 6, table_type: 'LONG_6', grid_x: 3, grid_y: 2 },
      { id: 6, table_number: 6, capacity: 2, table_type: 'ROUND_2', grid_x: 5, grid_y: 2 },
      { id: 7, table_number: 7, capacity: 4, table_type: 'RECT_4', grid_x: 0, grid_y: 4 },
      { id: 8, table_number: 8, capacity: 6, table_type: 'LONG_6', grid_x: 2, grid_y: 4 },
      { id: 9, table_number: 9, capacity: 4, table_type: 'RECT_4', grid_x: 4, grid_y: 5 }
    ],
    reservations: [
      { id: 1, table_id: 2, customer_name: 'Marguerite Hale', customer_phone: '(555) 014 8820', reservation_date: date, start_time: 18, duration: 3 },
      { id: 2, table_id: 5, customer_name: 'Ivo Brandt', customer_phone: '(555) 902 1177', reservation_date: date, start_time: 19, duration: 3 },
      { id: 3, table_id: 7, customer_name: 'Dala Okonkwo', customer_phone: '(555) 771 3390', reservation_date: date, start_time: 21, duration: 2 },
      { id: 4, table_id: 3, customer_name: 'Petra Lindqvist', customer_phone: '(555) 336 0042', reservation_date: date, start_time: 12, duration: 2 }
    ],
    next_id: 100
  }
}
seed()

function respond(value) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (demo_flags.force_network) {
        demo_flags.force_network = false
        reject({ status: 0, message: 'Network error — could not reach the server' })
        return
      }
      resolve(typeof value === 'function' ? value() : value)
    }, LATENCY)
  })
}

const clone = (value) => JSON.parse(JSON.stringify(value))

function overlaps(reservation, date, start_time, duration) {
  return (
    reservation.reservation_date === date &&
    reservation.start_time < start_time + duration &&
    start_time < reservation.start_time + reservation.duration
  )
}

/** GET /api/tables */
export function fetch_tables() {
  return respond(() => clone(db.tables))
}

/** GET /api/availability?date=&start_time=&duration=&party_size= */
export function fetch_availability({ date, start_time, duration, party_size }) {
  return respond(() =>
    db.tables.map((table) => {
      const is_reserved = db.reservations.some(
        (r) => r.table_id === table.id && overlaps(r, date, start_time, duration)
      )
      return {
        table_id: table.id,
        is_reserved,
        fits_party: table.capacity >= party_size,
        is_available: !is_reserved && table.capacity >= party_size
      }
    })
  )
}

/** GET /api/reservations?date= */
export function fetch_reservations(date) {
  return respond(() =>
    clone(db.reservations.filter((r) => !date || r.reservation_date === date))
      .sort((a, b) => a.start_time - b.start_time)
  )
}

/** POST /api/reservations */
export function create_reservation(payload) {
  return respond(() => {
    const conflict =
      demo_flags.force_conflict ||
      db.reservations.some(
        (r) =>
          r.table_id === payload.table_id &&
          overlaps(r, payload.reservation_date, payload.start_time, payload.duration)
      )
    if (conflict) {
      demo_flags.force_conflict = false
      throw { status: 409, message: 'This table was just booked. Pick another.' }
    }
    const reservation = { id: db.next_id++, ...payload }
    db.reservations.push(reservation)
    return clone(reservation)
  })
}

/** POST /api/tables */
export function create_table(payload) {
  return respond(() => {
    const taken =
      demo_flags.force_conflict ||
      db.tables.some(
        (t) =>
          t.table_number === payload.table_number ||
          (t.grid_x === payload.grid_x && t.grid_y === payload.grid_y)
      )
    if (taken) {
      demo_flags.force_conflict = false
      throw { status: 409, message: 'That table number or position is already taken.' }
    }
    const table = { id: db.next_id++, ...payload }
    db.tables.push(table)
    return clone(table)
  })
}

/** DELETE /api/tables/:id */
export function delete_table(table_id) {
  return respond(() => {
    const date = today_iso()
    const has_bookings = db.reservations.some(
      (r) => r.table_id === table_id && r.reservation_date >= date
    )
    if (has_bookings) throw { status: 400, message: 'Cannot delete — has active bookings' }
    db.tables = db.tables.filter((t) => t.id !== table_id)
    return { ok: true }
  })
}

/** Demo helpers — not part of the real API. */
export function reset_data() {
  seed()
}
export function clear_floor() {
  db.tables = []
  db.reservations = []
}
