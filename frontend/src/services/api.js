/**
 * API layer — mirrors the endpoints in openapi.yaml.
 * Shapes are snake_case, hours are integers, dates are ISO (YYYY-MM-DD).
 * Every exported function resolves the same shape and rejects with
 * { status, message } whether USE_MOCKS is on or off, so components
 * never need to know which one is active.
 */

export const USE_MOCKS = false

// VITE_API_BASE is set at build time (see render.yaml, which links it
// to the backend service's host) to just a hostname, e.g.
// "restaurant-backend.onrender.com" - no scheme, no /api suffix.
// Falls back to the local dev backend when unset.
const API_HOST = import.meta.env.VITE_API_BASE
// Exported so the UI can link to the backend directly (e.g. to nudge
// a sleeping free-tier instance awake) without duplicating this logic.
export const API_ORIGIN = API_HOST ? `https://${API_HOST}` : 'http://localhost:8000'
const API_BASE = `${API_ORIGIN}/api`

export const today_iso = () => new Date().toISOString().slice(0, 10)

export const TYPE_CAPACITY = { ROUND_2: 2, RECT_4: 4, LONG_6: 6 }

/** Demo switches the UI can flip to exercise error paths (mock mode only). */
export const demo_flags = { force_conflict: false, force_network: false }

// ---------------------------------------------------------------------------
// Real backend (USE_MOCKS = false)
// ---------------------------------------------------------------------------

async function real_request(path, { method = 'GET', params, body } = {}) {
  const query = params
    ? '?' + new URLSearchParams(
        Object.entries(params).filter(([, v]) => v !== undefined && v !== null)
      )
    : ''

  let response
  try {
    response = await fetch(`${API_BASE}${path}${query}`, {
      method,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined
    })
  } catch {
    throw { status: 0, message: 'Network error — could not reach the server' }
  }

  if (!response.ok) {
    let message = `Request failed with status ${response.status}.`
    try {
      const error_body = await response.json()
      message = error_body.detail || message
    } catch {
      // response had no JSON body — keep the generic message
    }
    throw { status: response.status, message }
  }

  if (response.status === 204) return null
  return response.json()
}

const real_fetch_tables = () => real_request('/tables')

const real_fetch_availability = ({ date, start_time, duration, party_size }) =>
  real_request('/availability', { params: { date, start_time, duration, party_size } })

const real_fetch_reservations = (date) => real_request('/reservations', { params: { date } })

const real_create_reservation = (payload) =>
  real_request('/reservations', { method: 'POST', body: payload })

const real_create_table = (payload) => real_request('/tables', { method: 'POST', body: payload })

const real_delete_table = (table_id) => real_request(`/tables/${table_id}`, { method: 'DELETE' })

// ---------------------------------------------------------------------------
// Mock, in-memory backend (USE_MOCKS = true)
// ---------------------------------------------------------------------------

const LATENCY = 200

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
      { id: 3, table_id: 7, customer_name: 'Dala Okonkwo', customer_phone: '(555) 771 3390', reservation_date: date, start_time: 21, duration: 1 },
      { id: 4, table_id: 3, customer_name: 'Petra Lindqvist', customer_phone: '(555) 336 0042', reservation_date: date, start_time: 12, duration: 2 }
    ],
    next_id: 100
  }
}
if (USE_MOCKS) seed()

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

const mock_fetch_tables = () => respond(() => clone(db.tables))

const mock_fetch_availability = ({ date, start_time, duration, party_size }) =>
  respond(() =>
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

const mock_fetch_reservations = (date) =>
  respond(() =>
    clone(db.reservations.filter((r) => !date || r.reservation_date === date))
      .sort((a, b) => a.start_time - b.start_time)
  )

const mock_create_reservation = (payload) =>
  respond(() => {
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

const mock_create_table = (payload) =>
  respond(() => {
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

const mock_delete_table = (table_id) =>
  respond(() => {
    const date = today_iso()
    const has_bookings = db.reservations.some(
      (r) => r.table_id === table_id && r.reservation_date >= date
    )
    if (has_bookings) throw { status: 400, message: 'Cannot delete — has active bookings' }
    db.tables = db.tables.filter((t) => t.id !== table_id)
    return { ok: true }
  })

/** Demo helpers — mock mode only, not part of the real API. */
export function reset_data() {
  if (USE_MOCKS) seed()
}
export function clear_floor() {
  if (USE_MOCKS) {
    db.tables = []
    db.reservations = []
  }
}

// ---------------------------------------------------------------------------
// Public API — dispatches to mock or real depending on USE_MOCKS
// ---------------------------------------------------------------------------

/** GET /api/tables */
export const fetch_tables = () => (USE_MOCKS ? mock_fetch_tables() : real_fetch_tables())

/** GET /api/availability?date=&start_time=&duration=&party_size= */
export const fetch_availability = (params) =>
  USE_MOCKS ? mock_fetch_availability(params) : real_fetch_availability(params)

/** GET /api/reservations?date= */
export const fetch_reservations = (date) =>
  USE_MOCKS ? mock_fetch_reservations(date) : real_fetch_reservations(date)

/** POST /api/reservations */
export const create_reservation = (payload) =>
  USE_MOCKS ? mock_create_reservation(payload) : real_create_reservation(payload)

/** POST /api/tables */
export const create_table = (payload) =>
  USE_MOCKS ? mock_create_table(payload) : real_create_table(payload)

/** DELETE /api/tables/:id */
export const delete_table = (table_id) =>
  USE_MOCKS ? mock_delete_table(table_id) : real_delete_table(table_id)
