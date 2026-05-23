# 🏍️ MotoGP Universe

เว็บแอพ MotoGP สร้างด้วย Flask + SQLite

## โครงสร้างโปรเจค
```
motogp/
├── app.py                  # Flask app หลัก
├── requirements.txt        # Dependencies
├── Procfile                # สำหรับ Deploy
├── render.yaml             # Render.com config
└── templates/
    ├── base.html           # Layout หลัก (navbar, footer)
    ├── index.html          # หน้าแรก
    ├── teams.html          # ตาราง Teams
    ├── form_teams.html     # ฟอร์ม Add/Edit Teams
    ├── merchandise.html    # ตาราง Merchandise
    ├── form_merchandise.html
    ├── tracks.html         # ตาราง Tracks
    ├── form_tracks.html
    ├── calendar.html       # ปฏิทินการแข่ง
    ├── form_calendar.html
    ├── results.html        # ผลการแข่งขัน
    ├── form_results.html
    └── compare.html        # เปรียบเทียบนักขับ
```

## วิธีรัน Local

```bash
# 1. ติดตั้ง dependencies
pip install -r requirements.txt

# 2. รัน
python app.py

# 3. เปิดเบราเซอร์
# http://127.0.0.1:5000
```

## วิธี Deploy บน Render.com (ฟรี)

1. Push โค้ดขึ้น GitHub
2. ไปที่ https://render.com → New Web Service
3. เชื่อม GitHub repo
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `gunicorn app:app`
6. คลิก Deploy!

## Features
- หน้าแรก: ภาพรวม standings + upcoming races + results
- Teams: CRUD ครบ (เพิ่ม/แก้ไข/ลบ)
- Merchandise: ราคาสินค้าแต่ละทีม
- Tracks: ข้อมูลสนามทั่วโลก
- Calendar: ปฏิทินการแข่ง 2025
- Results: ผลการแข่งขัน
- Compare: เปรียบเทียบนักขับ/ทีม
- Database: SQLite (auto-init พร้อม seed data)
