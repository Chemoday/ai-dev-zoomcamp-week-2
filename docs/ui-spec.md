# UI/UX Brief — Interactive Restaurant Table Reservation System

This document is a detailed frontend brief for an AI UI-generation tool
(Lovable, Bolt, Cursor, Claude Code, etc.). Read it **together with**
`product-spec.md`:

- Section 2 (Tech Stack) — Vue 3 `<script setup>`, Vite, Tailwind CSS
- Section 4 (API Specification) — the exact data shapes and endpoints
- Section 8 (Guardrails) — snake_case fields, no Vue 2 syntax, no
  external drag/drop or layout libraries, integer hours / ISO dates only

This document does not redefine the API or business rules — it exists
to enumerate every screen, state, and transition a complete prototype
needs, so nothing is left as an unstated "happy path" guess.

---

## 1. Global layout & navigation model

Single-page app, desktop-first, **no router needed** — there is exactly
one page. "Guest view" vs "Staff view" is a client-side role toggle
(a reactive `ref`), not a route or separate page load. Switching roles
re-renders the same Filter Bar + Floor Grid region with different
data/styling — it does not navigate away from it.

Persistent app shell:

```
┌─────────────────────────────────────────────┐
│ AppHeader (title, role switch)               │  <- always visible
├─────────────────────────────────────────────┤
│ FilterBar (date, time, duration, party size) │  <- always visible
├─────────────────────────────────────────────┤
│                                               │
│              FloorGrid (6×6)                 │  <- main content
│                                               │
├─────────────────────────────────────────────┤
│ (Staff only) Reservations list for the day   │  <- see Screen 3
└─────────────────────────────────────────────┘
Overlays (rendered above everything): Modal, Drawer, Toasts
```

---

## 2. Design tokens

Map these to Tailwind utility classes/config — don't hardcode hex
values inline in components.

**Color roles**
| Token | Purpose | Example Tailwind |
|---|---|---|
| `surface` | page/card background | `bg-white` / `bg-slate-50` |
| `border-default` | grid cell borders, dividers | `border-slate-200` |
| `text-primary` | headings, primary text | `text-slate-900` |
| `text-secondary` | helper/meta text | `text-slate-500` |
| `available` | table available & fits party | `bg-emerald-500` |
| `available-hover` | hover state of the above | `bg-emerald-600` |
| `too-small` | available but capacity < party size | `bg-slate-300` |
| `reserved` | occupied/reserved in selected window | `bg-rose-500` |
| `accent` | primary actions (confirm, submit) | `bg-indigo-600` |
| `danger` | destructive actions (delete) | `bg-rose-600` |
| `warning-surface` | demo-mode banner | `bg-amber-50` / `text-amber-800` |

**Typography scale**: page title `text-2xl font-semibold`, section
labels `text-sm font-medium text-secondary`, body `text-sm`, table
cell labels `text-xs font-medium`.

**Spacing**: grid gap `gap-3`, card padding `p-4`, modal padding `p-6`.

**Elevation**: cards/modals `shadow-md`, drawer `shadow-xl`, hover-lift
tables `shadow-lg` on hover.

---

## 3. Screen catalog

### 3.1 Guest reservation screen (default view)
- **Purpose**: guest picks date/time/party size and books an available table
- **Components**: `AppHeader`, `FilterBar`, `FloorGrid` (guest mode)
- **Data needed**: `GET /api/tables`, `GET /api/availability`
- **Entry point**: default screen on load
- **Exit points**: opens `ReservationModal` on clicking an available table

### 3.2 Staff floor management screen
- **Purpose**: staff inspects the floor for a date/time window, places
  new tables, manages/deletes existing ones
- **Components**: `AppHeader`, `FilterBar` (date/time still apply — see
  §9 for why), `FloorGrid` (staff mode)
- **Data needed**: `GET /api/tables`, `GET /api/availability`,
  `GET /api/reservations?date=...`
- **Entry point**: role switch from Guest view (see §1) — first switch
  triggers the one-time demo-mode banner (§8)
- **Exit points**: empty cell → `AddTableModal`; occupied cell →
  `AdminDrawer`

### 3.3 Staff reservations list (day view) — addition beyond spec §5
Not explicitly in `product-spec.md` §5, but a natural companion to the
grid using an endpoint the spec already defines
(`GET /api/reservations?date=`): a scrollable list/table below or beside
the FloorGrid in staff mode, showing all bookings for the selected date
— customer name, table number, start/end time, party context. Clicking
a row opens the same `AdminDrawer` as clicking its table on the grid.
Purpose: lets staff scan the whole day without hunting across the grid.
This is additive polish, not a requirement — flag it as optional if the
generation tool needs to cut scope.

---

## 4. Modals & overlays catalog

### 4.1 ReservationModal (guest booking)
- **Trigger**: click an available (green) table cell in guest view
- **Fields**: table info (read-only: number, capacity, type),
  `customer_name` (required), `customer_phone` (required), reservation
  date/time/duration (pre-filled from FilterBar, editable)
- **States**:
  - *default*: empty form, submit disabled until required fields valid
  - *validating*: inline field errors (empty name, malformed phone) —
    see form-error shake in §7
  - *submitting*: submit button shows a spinner, form disabled
  - *success*: success checkmark animation (§7), toast fires, modal
    auto-closes, grid cell turns red
  - *conflict error*: table was booked by someone else in the interim
    (`409`) — inline banner in the modal: "This table was just booked.
    Pick another." Modal stays open, grid refetches in the background.

### 4.2 AddTableModal (staff)
- **Trigger**: click an empty cell in staff view (the dashed `+` cell)
- **Fields**: `table_number`, `capacity`, `table_type` (select:
  `ROUND_2` / `RECT_4` / `LONG_6`, capacity can auto-fill from type)
- **States**: default, validating (duplicate table_number, missing
  fields), submitting, success (modal closes, new cell pop-in — §7),
  conflict error (`409`, coordinate occupied — shouldn't normally
  happen since only empty cells are clickable, but handle it
  defensively for concurrent-staff-edits)

### 4.3 AdminDrawer (staff table details)
- **Trigger**: click an occupied cell in staff view
- **Slides in from the right** (§7), does not block interaction with
  the rest of the page (it's a drawer, not a modal)
- **Content**: table header (number, type, capacity), list of that
  table's active/upcoming bookings (customer, date, time, duration),
  a "Delete Table" button
- **States**:
  - *default*: shows bookings list (or "No active bookings" empty
    state if none)
  - *delete confirm*: clicking "Delete Table" swaps the button region
    for an inline confirm ("Are you sure? [Cancel] [Confirm delete]")
    rather than a second modal
  - *delete blocked*: if the table has active/future bookings, the
    delete action is disabled with a tooltip/inline note: "Cannot
    delete — has active bookings" (matches the `400` the backend
    returns); do not let the user reach a failed request for this case
  - *delete success*: drawer closes, cell fades out/collapses (§7),
    toast fires

---

## 5. Component state catalog

**FloorGrid cell — guest mode**
| State | Appearance |
|---|---|
| Empty | inactive/blank slot |
| Available & fits party | `available` color, clickable, hover-lift |
| Available but too small | `too-small` color, disabled, "Too small" badge |
| Reserved in window | `reserved` color, disabled, "Reserved" badge |

**FloorGrid cell — staff mode**
| State | Appearance |
|---|---|
| Empty | dashed border, `+` icon, clickable |
| Has table | shows table_number + capacity badge, clickable to open drawer |

**Buttons**: default / hover / focus-visible (keyboard outline) /
disabled (reduced opacity, no pointer events) / loading (spinner,
disabled)

**Form fields**: default / focused (accent ring) / invalid (red ring +
inline error text below) / disabled

---

## 6. Transitions & animations catalog

| Trigger | Effect | Notes |
|---|---|---|
| Hover an available table (guest) | lift + shadow | `transform: translateY(-2px)`, transition ~150ms |
| FilterBar value changes | grid cells cross-fade to new availability colors | brief pulse/skeleton during the ~200ms mock network delay |
| Modal open/close | fade + scale-in overlay, backdrop dim | ~200ms ease-out in, ~150ms ease-in out |
| Drawer open/close | slide in/out from the right | ~250ms ease-out |
| Toast appear/dismiss | slide-in from top-right, auto-dismiss after ~3s with fade-out | stack multiple toasts vertically |
| New table added (staff) | cell pop-in (`scale: 0 → 1`) | ~200ms ease-out |
| Table deleted | cell fade-out + height/width collapse | ~200ms |
| Form validation failure | shake animation on the invalid field/button | short, ~300ms, small amplitude |
| Reservation success | checkmark icon animates in before modal auto-closes | ~600ms total, then close |
| Role switch (Guest ⇄ Staff) | grid re-colors/re-labels in place | no page transition; optional brief cross-fade on the grid region |

---

## 7. Feedback & notifications

**Toasts** (transient, auto-dismiss): "Reservation confirmed", "Table
added", "Table deleted", "Reservation canceled", "Network error — could
not reach the server" (this one persists until dismissed or retried,
does not auto-dismiss).

**Banners** (persistent until dismissed or condition changes):
- One-time demo-mode banner on first switch to Staff view: *"Demo mode:
  switched to Staff view without full authentication"* (per spec §5.1)
- Network error banner if the initial `GET /api/tables` fails on load,
  with a "Retry" action (see §8)

---

## 8. Empty / loading / error states

- **First load (skeleton)**: while the initial `GET /api/tables` +
  `GET /api/availability` resolve, show skeleton/placeholder cells in
  the grid shape rather than a blank screen
- **Empty floor**: no tables exist yet — guest view shows a friendly
  empty message ("No tables have been set up yet — check back soon");
  staff view shows the full grid of empty `+` cells with a hint to
  start adding tables
- **Fully booked**: every table is either reserved or too small for
  the selected filters — guest view shows a message above/below the
  grid: "No tables available for this time — try a different time or
  party size", grid still renders (all red/gray) so the user can see why
- **Network failure**: initial load or a mutation request fails —
  show a retry-capable error state (banner for initial load, inline
  error for a form submission) rather than a silent failure

---

## 9. User flow walkthroughs

**Guest books a table**
1. Land on Guest reservation screen; default filters pre-filled
2. Adjust date/time/duration/party size in FilterBar → grid re-colors
3. Click a green (available, fits) table → `ReservationModal` opens,
   pre-filled with the current filter values
4. Fill name + phone → submit → success animation → toast → modal
   closes → that cell is now red

**Staff adds a table**
1. Switch role to Staff (first time: demo-mode banner appears)
2. Pick a date/time (used only to check the grid isn't mid-reservation
   for that slot, not required to add a table)
3. Click an empty `+` cell → `AddTableModal` opens
4. Fill table_number/capacity/type → submit → success → new cell pop-in

**Staff deletes a table (blocked path)**
1. In Staff view, click an occupied cell → `AdminDrawer` slides in
2. Drawer shows the table has active bookings
3. Click "Delete Table" → delete is disabled/blocked with an inline
   explanation, because of those active bookings (no failed request is
   ever sent — the UI prevents it)

**Staff deletes a table (success path)**
1. Same as above, but the table has no active/future bookings
2. Click "Delete Table" → inline confirm ("Confirm delete") → confirm
   → drawer closes, cell fades out/collapses, toast fires

---

## 10. Out of scope

Matches `product-spec.md` non-goals — do not design screens for:
- staff login/authentication
- real SMS/push notifications to guests
- advance online reservations beyond the same-day booking flow modeled here
- payment collection
- multi-restaurant / multi-location switching
- a dedicated mobile/responsive layout (desktop-first only, per spec §1)
