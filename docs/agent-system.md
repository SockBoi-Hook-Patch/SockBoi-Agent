# SockBoi Agent System / ระบบ Agent ของ SockBoi AI

## สถานะ v0.3.0
รุ่นนี้เพิ่มฐานความรู้และ Tool Registry แต่ยังเป็นระบบวางแผน ไม่ใช่ Agent ที่รัน Pentest จริงโดยอัตโนมัติ

## บทบาท Agent
- **SockBoi Core:** ประสานงานและจัดการวงจร Engagement (แผนพัฒนา)
- **SockBoi Guard:** ตรวจ Scope, Authorization, Approval และ Policy
- **SockBoi Recon:** วิเคราะห์ Asset Inventory และ Metadata ที่ผู้ใช้ส่งให้ (แผนพัฒนา)
- **SockBoi Hunter:** วางแผนตรวจ Web Configuration
- **SockBoi API:** วิเคราะห์ API Schema ที่ผู้ใช้ส่งให้
- **SockBoi Network:** วิเคราะห์ Network Inventory ที่ผู้ใช้ส่งให้ โดยไม่สแกนพอร์ต
- **SockBoi Analyst:** ตรวจสอบความครบถ้วนและ Integrity ของ Evidence
- **SockBoi Report:** สร้างรายงาน (แผนพัฒนา)

## Knowledge Layer
Endpoint `POST /knowledge/ingest` รับ Markdown สูงสุด 256 KB ต่อเอกสาร และคำนวณ SHA-256 เพื่อระบุเนื้อหา เอกสารค้นหาได้ผ่าน `GET /knowledge/search` ด้วย lexical keyword scoring

**ข้อกำหนดสำคัญ:** เนื้อหาที่นำเข้าทั้งหมดเป็น Untrusted Reference Data ไม่ใช่ System Prompt หรือคำสั่ง Tool และไม่สามารถแก้ Scope, Policy หรือ Approval ได้ รุ่นนี้ยังไม่มีการดึงข้อมูลจาก Git repository โดยตรง

## Typed Tool Registry
`GET /tools` แสดงรายการเครื่องมือพร้อม JSON input schema ได้แก่:
- `knowledge.search`
- `evidence.sha256`
- `scope.inspect`

รายการเหล่านี้เป็น Catalog เท่านั้น `execution_enabled=false` ทุกตัว ไม่มี generic shell หรือ arbitrary MCP invocation

## Approval Model
Approval ระบุ Engagement, Target, Technique ID และผู้ร้องขอ การอนุมัติ Active/State-changing ต้อง:
1. Target อยู่ใน Scope แบบ deterministic
2. Approval เป็นของ Engagement เดียวกัน
3. Target ตรงกับ Approval แบบ exact match
4. Technique ID ตรงกับ Approval
5. ผู้อนุมัติไม่ใช่ผู้ร้องขอ
6. Approval ยังไม่หมดอายุ

## Evidence Integrity
`POST /evidence/hash` คืน SHA-256 digest ของข้อความที่ส่งมาเท่านั้น ไม่บันทึก raw evidence ลง Store

## ข้อจำกัด
Knowledge Library และ Store เป็น In-memory; ไม่มี Authentication, RBAC, Tenant Isolation, PostgreSQL, MCP Runtime, Browser/ZAP Adapter หรือ LLM Runtime ในรุ่นนี้
