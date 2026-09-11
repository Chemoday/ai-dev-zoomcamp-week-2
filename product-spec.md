# 🍽️ Interactive Restaurant Table Reservation System (Full-Stack MVP)

## 1. Project Overview & Scope
A desktop-first interactive web application for restaurant table reservations and floor management.
* **Client View:** Allows guests to select a date, time slot, duration, and party size to visually book an available table on an interactive restaurant floor map.
* **Staff/Admin View:** Allows restaurant managers to inspect live table availability, visually add new tables to empty floor coordinates, and manage/delete existing tables with reservation safeguards.
* **Core Philosophy:** Highly reactive frontend, clean modular service layer, desktop-focused, robust error handling, and simple data models without over-engineering.

---

## 2. Technology Stack & Directory Structure

* **Frontend:** Vue 3 (Composition API with `<script setup>`), Vite, Tailwind CSS.
* **Backend:** Python 3.10+, FastAPI, SQLite, SQLAlchemy (synchronous ORM), Pydantic v2.
* **Development Workflow:** Contract-driven development:
  1. Frontend UI + Decoupled Mock Service Layer (`src/services/api.js`).
  2. FastAPI Backend satisfying the exact contract.
  3. Integration (flipping `USE_MOCKS = false`).

### Target Directory Layout
```text
restaurant-reservation/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI entry point, CORS, and startup events
│   │   ├── database.py        # SQLite engine & session setup
│   │   ├── models.py          # SQLAlchemy ORM models
│   │   ├── schemas.py         # Pydantic validation schemas
│   │   └── crud.py            # Database queries and conflict validation
│   ├── requirements.txt
│   └── restaurant.db          # Auto-generated SQLite file
│
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── AppHeader.vue        # App title & Role switch toggle (Guest/Staff)
│   │   │   ├── FilterBar.vue        # Date, time, duration, and guests selectors
│   │   │   ├── FloorGrid.vue        # 6x6 CSS Grid container
│   │   │   ├── TableCell.vue        # Visual cell component (Empty vs Table SVG/card)
│   │   │   ├── ReservationModal.vue # Guest booking form dialog
│   │   │   └── AdminDrawer.vue      # Staff actions drawer (manage/delete tables)
│   │   ├── services/
│   │   │   └── api.js               # Central API layer (Mock store <-> Real HTTP)
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
└── PROJECT_SPEC.md
```

---

## 3. Business Logic & Operational Constraints

1. **Floor Plan (CSS Grid):**
   * Dimensions: Fixed **$6 \times 6$ matrix** (36 cells total, indexed `x=0..5`, `y=0..5`).
   * **Atomic Unit Rule:** Each table occupies exactly **one** cell coordinate `(grid_x, grid_y)`.
   * **Visual Table Types:**
     * `ROUND_2`: Circular table, 2 seats capacity.
     * `RECT_4`: Square/rectangular table, 4 seats capacity.
     * `LONG_6`: Elongated table, 6 seats capacity.
2. **Operating Hours & Time Slot Logic:**
   * Operating Hours: `10:00` to `22:00` (12 hourly slots: `10, 11, ..., 21`).
   * Time unit: Integer hours (`10`, `14`, `18`).
   * Duration: `1` to `4` hours. Max valid start hour is `21` (for a 1-hour slot).
   * Date Format: Strictly ISO date strings (`YYYY-MM-DD`). No JavaScript `Date` timezone objects.
3. **Availability & Overlap Algorithm:**
   For a requested target date $D$, start hour $S_{new}$, and duration $L$ (where $E_{new} = S_{new} + L$):
   A table is **unavailable** if there exists an active reservation for that table on date $D$ with start hour $S_{res}$ and end hour $E_{res}$ satisfying:
   $$\text{NOT } (E_{new} \le S_{res} \lor S_{new} \ge E_{res})$$
4. **Table Deletion Protection:**
   Staff cannot delete a table if it has active reservations scheduled for today or future dates. The backend must reject this with `400 Bad Request`.

---

## 4. API Specification & Data Contracts

All endpoints communicate via JSON using strict **`snake_case`** field names.

### 4.1. Core Entities

#### Table Schema
```json
{
  "id": 1,
  "table_number": "T-1",
  "capacity": 4,
  "table_type": "RECT_4",
  "grid_x": 1,
  "grid_y": 2
}
```

#### Reservation Schema
```json
{
  "id": 101,
  "table_id": 1,
  "customer_name": "John Doe",
  "customer_phone": "+1234567890",
  "reservation_date": "2023-11-20",
  "start_time": 18,
  "duration": 2,
  "end_time": 20
}
```

### 4.2. REST Endpoints

* **`GET /api/tables`**
  * Description: Fetch all physical tables on the floor grid.
  * Response: `Table[]`

* **`POST /api/tables`**
  * Description: Create/place a new table on the grid (Staff only).
  * Request Body:
    ```json
    {
      "table_number": "T-6",
      "capacity": 2,
      "table_type": "ROUND_2",
      "grid_x": 4,
      "grid_y": 1
    }
    ```
  * Response: Created `Table` object.
  * Errors: `409 Conflict` if coordinate `(grid_x, grid_y)` is already occupied.

* **`DELETE /api/tables/{id}`**
  * Description: Delete an existing table (Staff only).
  * Response: `{"success": true, "message": "Table deleted successfully"}`
  * Errors: `400 Bad Request` if table has future reservations (`{"detail": "Cannot delete table with active bookings."}`).

* **`GET /api/availability?date=YYYY-MM-DD&start_time=18&duration=2`**
  * Description: Check availability for all tables for the specified time window.
  * Response: Dictionary mapping `table_id` to boolean availability:
    ```json
    {
      "1": true,
      "2": false,
      "3": true
    }
    ```

* **`POST /api/reservations`**
  * Description: Book a table.
  * Request Body:
    ```json
    {
      "table_id": 1,
      "customer_name": "Jane Smith",
      "customer_phone": "+1987654321",
      "reservation_date": "2023-11-20",
      "start_time": 18,
      "duration": 2
    }
    ```
  * Response: Created `Reservation` object.
  * Errors: `409 Conflict` if table is already booked for any overlapping hour.

* **`GET /api/reservations?date=YYYY-MM-DD`**
  * Description: Fetch all reservations for a given date (Staff view).
  * Response: `Reservation[]`

* **`DELETE /api/reservations/{id}`**
  * Description: Cancel an active reservation.
  * Response: `{"success": true}`

---

## 5. UI/UX Specifications

### 5.1. Header & Role Switching
* Header displays the brand title and an interactive switch button: `[ Switch to Staff View ]` / `[ Switch to Guest View ]`.
* Switching to Staff view triggers a non-blocking dialog/banner: *"Demo mode: switched to Staff view without full authentication"*.

### 5.2. Filter Bar (Reactive Controls)
* Inputs:
  * **Date Picker:** Defaults to current date (`YYYY-MM-DD`).
  * **Start Time:** Dropdown selector from `10:00` to `21:00`. Defaults to `18` (18:00).
  * **Duration:** Dropdown selector (`1 hour`, `2 hours`, `3 hours`, `4 hours`). Defaults to `2`.
  * **Party Size:** Dropdown selector (`1` to `6` guests). Defaults to `2`.
* *Behavior:* Any change to these controls triggers an immediate, reactive refetch of table availability.

### 5.3. Interactive Floor Grid ($6 \times 6$)
* Rendered via CSS Grid (`grid-template-columns: repeat(6, minmax(0, 1fr))`).
* Total 36 cells.
* **Guest View States:**
  * Empty cell: Clean, inactive background slot.
  * Table (Available & `capacity >= party_size`): Highlighted in **Emerald Green**, clickable, hover lift effect.
  * Table (Available but `capacity < party_size`): Rendered in **Muted Gray**, disabled, badge *"Too small"*.
  * Table (Occupied/Reserved in selected window): Rendered in **Rose Red**, disabled, badge *"Reserved"*.
* **Staff View States:**
  * Empty cell: Displays a subtle dashed border with a `+` icon. Clicking prompts a mini modal to place a table (`table_number`, `capacity`, `table_type`).
  * Table cell: Displays table info + an indicator badge. Clicking opens `AdminDrawer` showing active bookings and a *"Delete Table"* action.

---

## 6. Implementation Roadmap

### Phase 1: Frontend First with Mock Layer (Priority)
1. Initialize Vite project with Vue 3 and Tailwind CSS.
2. Implement `src/services/api.js` containing an in-memory/`localStorage` reactive state:
   * 5 default tables placed on coordinates.
   * 2 initial reservations.
   * Async methods simulating network delays (200ms) returning Promises matching Section 4.
3. Build Vue components:
   * `AppHeader.vue`, `FilterBar.vue`, `FloorGrid.vue`, `TableCell.vue`.
   * `ReservationModal.vue` for guest reservation submissions.
   * `AdminDrawer.vue` for table additions and deletions.
4. Verify complete client-side reactivity (changing party size, booking a slot, toggling roles, adding tables).

### Phase 2: FastAPI Backend Implementation
1. Initialize Python virtual environment and install dependencies:
   `fastapi`, `uvicorn[standard]`, `sqlalchemy`, `pydantic`.
2. Configure `backend/app/database.py` with SQLite (`sqlite:///./restaurant.db`).
3. Define ORM models in `backend/app/models.py` (`Table`, `Reservation`).
4. Define Pydantic schemas in `backend/app/schemas.py`.
5. Implement endpoints in `backend/app/main.py` matching Section 4.
6. Add CORS middleware allowing all origins (`["*"]`).
7. Implement startup database initialization and automated table seeding (see Section 7).

### Phase 3: Integration & Final Delivery
1. In `frontend/src/services/api.js`, set `const USE_MOCKS = false`.
2. Replace mock methods with standard `fetch()` or `axios` calls directed to `http://localhost:8000/api`.
3. Test end-to-end user journeys:
   * Reserve a table from Guest view -> verify status turns Red -> verify row appears in SQLite database.
   * Switch to Staff view -> delete a table -> verify deletion safety triggers if active bookings exist.

---

## 7. Operational Details, Database Seeding & Setup

### 7.1. Database Initialization & Seeding Rules
* **No Alembic:** Do NOT use migration tools. Rely on `Base.metadata.create_all(bind=engine)` inside the FastAPI startup/lifespan handler.
* **Automatic Seed:** On startup, if the `tables` table contains 0 rows, populate it with 5 initial tables:
  * Table 1: `table_number: "T-1"`, `capacity: 2`, `table_type: "ROUND_2"`, `grid_x: 1`, `grid_y: 1`
  * Table 2: `table_number: "T-2"`, `capacity: 2`, `table_type: "ROUND_2"`, `grid_x: 1`, `grid_y: 4`
  * Table 3: `table_number: "T-3"`, `capacity: 4`, `table_type: "RECT_4"`, `grid_x: 3`, `grid_y: 1`
  * Table 4: `table_number: "T-4"`, `capacity: 4`, `table_type: "RECT_4"`, `grid_x: 3`, `grid_y: 4`
  * Table 5: `table_number: "T-5"`, `capacity: 6`, `table_type: "LONG_6"`, `grid_x: 5`, `grid_y: 2`

### 7.2. Quickstart Execution Commands

#### Backend Setup:
```bash
cd backend
python -m venv venv
# Linux / macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install fastapi "uvicorn[standard]" sqlalchemy pydantic
uvicorn app.main:app --reload --port 8000
```
*Swagger API Documentation will be available at:* `http://localhost:8000/docs`

#### Frontend Setup:
```bash
cd frontend
npm install
npm run dev
```
*Frontend will be available at:* `http://localhost:5173`

---

## 8. Guardrails for AI Code Generation
* **Field Naming:** Always use `snake_case` in JSON payloads and responses (`table_number`, not `tableNumber`).
* **Vue Syntax:** Use strictly Vue 3 `<script setup>` SFC syntax. Do NOT generate Vue 2 Options API code.
* **CSS Layout:** Use plain Tailwind CSS Grid (`grid grid-cols-6 gap-3`). Do NOT install external drag-and-drop or layout packages.
* **Time/Date Safety:** Do NOT use complex JS `Date` objects for calculations. Use integer hours (`10..21`) and simple ISO strings (`YYYY-MM-DD`).