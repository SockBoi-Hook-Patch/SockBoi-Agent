# SockBoi Agent

**แพลตฟอร์ม AI Agent สำหรับงาน Cybersecurity Assessment และ Full-spectrum Pentest แบบแยก Agent + Skills + MCP**

> สถานะ: Developer Preview ที่กำลังพัฒนา โค้ดปัจจุบันยังเป็น Planner, Knowledge API และ Tool Catalogue ไม่ใช่ระบบ Pentest อัตโนมัติที่เชื่อมต่อเครื่องมือจริง

## แนวคิด
SockBoi Agent แบ่งเป็น 4 ชั้น:
1. **Agent Core** — วางแผน แบ่งงาน และประสานงาน Specialist Agents
2. **Skills** — Playbook สำหรับ Web, API, Network, Source Code, Cloud และงานประเมินอื่น ๆ
3. **MCP** — มาตรฐานเชื่อมต่อ Browser, ZAP, Burp และเครื่องมือภายนอกผ่าน Schema ที่กำหนด
4. **Policy Engine** — ตรวจ Scope, Authorization, Approval และ Audit ก่อนเรียก Tool

## โครงสร้าง
ดู [Agent](agent/README.md), [Skills](skills/README.md), [MCP](mcp/README.md) และ [Roadmap](docs/roadmap.md)

## ติดตั้ง
ต้องใช้ Python 3.12 ขึ้นไป

```bash
git clone https://github.com/SockBoi-Hook-Patch/SockBoi-Agent.git
cd SockBoi-Agent
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn sockboi.main:app --reload
```

Windows PowerShell: ใช้ `.venv\\Scripts\\Activate.ps1` เพื่อเปิด virtual environment

เปิด API docs ที่ http://127.0.0.1:8000/docs

## ความสามารถที่มีในโค้ดปัจจุบัน
- Multi-Agent assessment planner แบบ deterministic
- นำเข้าและค้นหา Markdown Knowledge
- Typed Tool Catalogue โดยปิดการ execute
- Approval ผูกกับ Engagement, Target และ Technique
- SHA-256 Evidence Digest
- Scope validation และ Audit events

## ข้อจำกัด
ยังไม่มี Authentication, RBAC, Tenant Isolation, PostgreSQL persistence, MCP Runtime, Browser/ZAP/Burp execution หรือ LLM Runtime ข้อมูลยังเก็บในหน่วยความจำ อย่าเปิด API ให้เครือข่ายที่ไม่น่าเชื่อถือ และใช้เฉพาะระบบที่ได้รับอนุญาตเป็นลายลักษณ์อักษรเท่านั้น

## ภาษา
เอกสารภาษาอังกฤษอยู่ที่ [README.md](README.md)
