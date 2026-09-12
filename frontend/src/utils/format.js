// Matches the backend's valid start_time range (product-spec.md section 3.2).
export const HOURS = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]

export const TYPE_LABEL = { ROUND_2: 'Round', RECT_4: 'Rect', LONG_6: 'Long' }

export const TYPE_NOTE = {
  ROUND_2: 'Round top, two stools facing each other.',
  RECT_4: 'Rectangular top, two stools per long side.',
  LONG_6: 'Long communal top, three stools per side.'
}

export function format_hour(hour) {
  const suffix = hour >= 12 ? 'PM' : 'AM'
  const base = hour % 12 === 0 ? 12 : hour % 12
  return `${base}:00 ${suffix}`
}

export function format_window(start_time, duration) {
  return `${format_hour(start_time)} – ${format_hour(start_time + duration)}`
}

export function format_day(date_iso) {
  return new Date(`${date_iso}T12:00:00`).toLocaleDateString(undefined, {
    weekday: 'long',
    month: 'short',
    day: 'numeric'
  })
}

/** Stable pseudo-random tilt so the floor reads as hand-placed, not gridded. */
export function tilt_for(table_id) {
  return ((table_id * 37) % 17) - 8
}
