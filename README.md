# SockBoi Agent

**Policy-first AI security assessment platform / แพลตฟอร์ม AI สำหรับช่วยประเมินความปลอดภัยไซเบอร์โดยยึดนโยบายและขอบเขตที่ได้รับอนุญาตเป็นหลัก**

> **สถานะ: v0.3.1 Developer Preview (รุ่นทดลองสำหรับนักพัฒนา)**  
> SockBoi Agent มีระบบวางแผนงานแบบ Multi-Agent, คลังความรู้ Markdown, รายการเครื่องมือแบบ typed registry, การผูก Approval กับเป้าหมายและเทคนิค และการคำนวณ SHA-256 สำหรับตรวจสอบความถูกต้องของหลักฐาน  
> **ข้อจำกัด:** ระบบยังไม่เรียกใช้ Scanner, Browser, MCP Server, LLM หรือเครื่องมือโจมตีจริง ข้อมูลยังเก็บในหน่วยความจำ และยังไม่มี Authentication, RBAC, Tenant Isolation หรือ PostgreSQL persistence ห้ามใช้เป็น Production

## ภาษา / Languages

- [English](#english)
- [ภาษาไทย](#ภาษาไทย)

## ภาษาไทย

### SockBoi Agent คืออะไร
SockBoi Agent เป็นแพลตฟอร์มต้นแบบสำหรับช่วยวางแผนและจัดการกระบวนการตรวจสอบความปลอดภัยไซเบอร์ โดยใช้ AI Agent หลายบทบาทร่วมกัน มีระบบกำหนดขอบเขต (Scope), ตรวจสอบสิทธิ์ (Authorization), ขออนุมัติก่อนการทดสอบเชิงรุก และบันทึก Audit Log

แนวคิดหลักคือให้ AI ช่วยวิเคราะห์และจัดลำดับงาน แต่การตัดสินใจด้านสิทธิ์และขอบเขตต้องผ่าน Policy Engine ที่ทำงานแบบ deterministic ไม่ให้โมเดลหรือไฟล์ความรู้เปลี่ยนกฎเอง

### ความสามารถใน v0.3.1
- **Multi-Agent Planner:** แบ่งงานให้ SockBoi Guard, Hunter, API, Network และ Analyst
- **Knowledge Ingestion:** นำเข้าเอกสาร Markdown และค้นหาด้วยคำสำคัญ เอกสารทั้งหมดถือเป็นข้อมูลอ้างอิงที่ไม่น่าเชื่อถือ (Untrusted) ไม่ใช่คำสั่ง
- **Typed Tool Registry:** แสดงรายการเครื่องมือที่อนุญาตและ schema ของ input โดยยังปิดการ execute เครื่องมือทั้งหมด
- **Approval Binding:** การอนุมัติ Active Check ต้องผูกกับ Engagement, Target และ Technique และผู้ขออนุมัติห้ามอนุมัติงานของตัวเอง
- **Evidence Integrity:** คำนวณ SHA-256 ของข้อมูลที่ส่งเข้ามา โดย API ไม่จัดเก็บเนื้อหาหลักฐาน
- **Scope Validation:** ตรวจสอบ Domain, URL, IP และ CIDR ตามขอบเขตที่กำหนด
- **Audit Events:** บันทึกเหตุการณ์สำคัญของ Engagement, Plan, Approval และ Policy

### ติดตั้งและเริ่มใช้งาน

ต้องใช้ Python 3.12 ขึ้นไป

```bash
git clone https://github.com/SockBoi-Hook-Patch/SockBoi-Agent.git
cd SockBoi-Agent
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
uvicorn sockboi.main:app --reload
```

เปิด API Docs ที่ http://127.0.0.1:8000/docs

### Workflow เบื้องต้น
1. สร้าง Engagement พร้อมเลขอ้างอิงหนังสืออนุญาตและรายการ Asset ที่ชัดเจน
2. เรียก Planner ด้วย Target ที่อยู่ใน Scope เท่านั้น
3. ตรวจสอบแผนและระดับความเสี่ยงของแต่ละ Step
4. ขอ Approval ที่ระบุ Target และ Technique ก่อน Active Check
5. ตรวจสอบ Audit Log และ Finding

### API สำคัญ
| Endpoint | หน้าที่ |
|---|---|
| `GET /health` | ตรวจสอบสถานะและเวอร์ชัน |
| `POST /engagements` | สร้าง Engagement |
| `POST /engagements/{id}/plan?target=...` | สร้างแผน Multi-Agent |
| `POST /engagements/{id}/approvals` | ขออนุมัติแบบผูก Target/Technique |
| `POST /approvals/{id}/decide` | อนุมัติหรือปฏิเสธ (ผู้ขออนุมัติอนุมัติตัวเองไม่ได้) |
| `POST /policy/check` | ตรวจสอบ Policy ก่อนดำเนินการ |
| `POST /knowledge/ingest` | นำเข้า Markdown |
| `GET /knowledge/search?query=...` | ค้นหาเอกสารความรู้ |
| `GET /tools` | ดู Typed Tool Registry |
| `POST /evidence/hash` (ส่ง JSON body: `{"content":"..."}`) | คำนวณ SHA-256 โดยไม่บันทึกเนื้อหา |

### ข้อจำกัดและความปลอดภัย
- เป็น Developer Preview ยังไม่มีระบบล็อกอินหรือแยกข้อมูลผู้ใช้
- Store ยังเป็น In-memory เมื่อปิดโปรเซสข้อมูลจะหาย
- Knowledge ที่นำเข้ามาเป็น Untrusted Input เสมอ ห้ามนำไป execute
- Tool Registry เป็น Catalog เท่านั้น ยังไม่มีการเชื่อมต่อ MCP Server หรือเรียกเครื่องมือจริง
- ไม่มี Arbitrary Shell, Reverse Shell, Credential Theft, Persistence, DoS หรือการทดสอบนอก Scope
- ห้ามเปิด API สู่เครือข่ายสาธารณะหรือใช้กับระบบจริงจนกว่าจะเพิ่ม Authentication, RBAC, Tenant Isolation และ Durable Storage

### แผนพัฒนาต่อ
- [x] API และ Policy Foundation
- [x] Multi-Agent Planner
- [x] Knowledge Ingestion และ Keyword Retrieval
- [x] Typed Tool Registry (ปิดการ Execute)
- [x] Approval Binding และ SHA-256 Evidence Digest
- [ ] PostgreSQL + Database Migrations
- [ ] Authentication, RBAC และ Tenant Isolation
- [ ] MCP Adapter แบบจำกัด Schema พร้อม Policy Gate
- [ ] Browser/ZAP Adapter ใน Sandbox พร้อม Egress Allowlist
- [ ] LLM Planner Provider และ Evaluation Suite
- [ ] Evidence Store และ Report Generator

## Product Architecture\n\nSockBoi Agent is organized into three modular layers: **Agent Core** (orchestration), **Skills** (versioned assessment playbooks), and **MCP** (typed integrations). The deterministic Policy Engine remains the authorization authority. See [Agent](agent/README.md), [Skills](skills/README.md), [MCP](mcp/README.md), and [Roadmap](docs/roadmap.md).\n\n## English

### Overview
SockBoi Agent is a developer-preview control plane for authorized security assessments. It coordinates specialist-agent planning while keeping scope and approval decisions in a deterministic policy layer.

### v0.3.1
- Deterministic multi-agent assessment planning.
- Markdown knowledge ingestion and keyword retrieval; imported content is untrusted reference data.
- Typed tool catalogue with execution disabled.
- Human approvals bound to engagement, exact target, and technique; self-approval is rejected.
- SHA-256 evidence digest endpoint that does not persist submitted content.
- Explicit scope validation and audit events.

### Quick start
Requires Python 3.12+.

```bash
git clone https://github.com/SockBoi-Hook-Patch/SockBoi-Agent.git
cd SockBoi-Agent
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn sockboi.main:app --reload
```

Open http://127.0.0.1:8000/docs.

### Important limitations
This is not a production-ready pentest runner. There is no authentication, tenant isolation, durable database, live MCP integration, browser/scanner execution, or LLM runtime. The store is in-memory. Do not expose it to untrusted networks.

See [docs/architecture.md](docs/architecture.md), [docs/agent-system.md](docs/agent-system.md), and [SECURITY.md](SECURITY.md).
