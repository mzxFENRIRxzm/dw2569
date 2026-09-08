## MoviePulse Django + ClickHouse Dashboard

โปรเจกต์นี้รัน Django ได้โดยไม่ต้องใช้ Docker โดยหน้า dashboard จะใช้ข้อมูล demo อัตโนมัติเมื่อยังเชื่อมต่อ ClickHouse ไม่ได้

### โหมดไม่ใช้ Docker

เปิด PowerShell ที่โฟลเดอร์ `dw2569` แล้วรัน:

```powershell
uv sync
New-Item -ItemType Directory -Force data
uv run python manage.py migrate
uv run python manage.py runserver
```

เปิดหน้า dashboard ที่ `http://127.0.0.1:8000/dashboard/`

โหมดนี้ไม่ต้องมี ClickHouse server และใช้ข้อมูล demo สำหรับการดูหน้าจอและทดสอบ live update

### ใช้ ClickHouse แบบ local

ถ้ามี ClickHouse Server ที่เครื่องหรือใน WSL ให้ตั้งค่าก่อนรันคำสั่ง setup:

```powershell
$env:CLICKHOUSE_HOST = "localhost"
$env:CLICKHOUSE_PORT = "8123"
$env:CLICKHOUSE_USER = "default"
$env:CLICKHOUSE_PASSWORD = ""
$env:CLICKHOUSE_DB = "default"

uv run python manage.py setup_clickhouse
uv run python manage.py seed_movies
uv run python manage.py runserver
```

เมื่อ ClickHouse ใช้งานได้ dashboard จะเปลี่ยนจาก `demo` เป็นข้อมูลจริงจากตาราง `movie_ratings` โดยอัตโนมัติ

### URL สำคัญ

- `/dashboard/` หน้าหลัก MoviePulse
- `/analytics/` หน้าหลักเดียวกัน
- `/analytics/data/` JSON endpoint สำหรับ event-driven refresh และรับข้อมูลใหม่

### ทดสอบการอัปเดตแบบ real-time

1. เปิด terminal ที่โฟลเดอร์ `dw2569` แล้วรัน `uv run python manage.py runserver`
2. เปิด browser สองแท็บที่ `http://127.0.0.1:8000/dashboard/`
3. ใช้ฟอร์ม `Add a movie rating` ในแท็บซ้าย
4. ดูแท็บขวา จะเห็น poster และ rating ใหม่ทันที

การอัปเดตใช้ `BroadcastChannel` และ `storage` event ระหว่างแท็บ ไม่มี `setInterval` หรือ client polling

### Project prompt

สร้าง Django project ชื่อ `dashboard` สำหรับแสดงคะแนนหนังแบบ live โดยใช้ poster เป็น visual หลัก เมื่อมีการเพิ่มหรือ update movie rating เดิม ให้คะแนนบน poster, spotlight และ rating ledger เปลี่ยนทันทีใน dashboard ที่เปิดอยู่ โดยใช้ event-driven browser updates (`BroadcastChannel`/`storage event`) และห้ามใช้ polling
