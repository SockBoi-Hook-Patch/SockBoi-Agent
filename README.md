# SockBoi Agent

**Policy-first AI Security Assessment Platform**  
แพลตฟอร์มช่วยวางแผน ประเมิน และจัดการงานตรวจสอบความปลอดภัยไซเบอร์ในระบบที่ได้รับอนุญาต โดยให้ Scope, Policy และ Human Approval เป็นตัวควบคุมหลัก

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/) [![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)](https://fastapi.tiangolo.com/) [![Security](https://img.shields.io/badge/Design-Policy--First-informational)](SECURITY.md)

> **สถานะโครงการ: Developer Preview — v0.4 security foundations**
>
> โค้ดใน branch `feat/v0.4-active-assessment-foundation` มี Authentication, RBAC, Tenant Isolation, SQLAlchemy persistence และ Action-bound Approval foundation แล้ว แต่ยัง **ไม่ใช่เครื่องมือ Pentest ที่สั่ง Scanner หรือยิงทดสอบเครือข่ายได้จริง** และยังไม่พร้อมใช้ Production
>
> หมายเหตุ: package metadata ปัจจุบันยังระบุเวอร์ชัน `0.3.1`; คำว่า v0.4 ใน README นี้หมายถึงชุดงาน foundation บน branch ดังกล่าว ไม่ใช่การประกาศ release/tag ใหม่

---

## สารบัญ | Contents

- [ภาษาไทย](#ภาษาไทย)
  - [SockBoi Agent คืออะไร](#sockboi-agent-คืออะไร)
  - [ทำอะไรได้บ้างในปัจจุบัน](#ความสามารถที่มีในโค้ดปัจจุบัน)
  - [สถาปัตยกรรม](#สถาปัตยกรรม)
  - [ติดตั้งและเริ่มใช้งาน](#ติดตั้งและเริ่มใช้งาน)
  - [ตั้งค่า API Authentication](#ตั้งค่า-api-authentication)
  - [Workflow การใช้งาน](#workflow-การใช้งาน)
  - [ตัวอย่าง Prompt สำหรับ AI](#ตัวอย่าง-prompt-สำหรับ-ai)
  - [API Endpoints](#api-endpoints)
  - [ข้อจำกัดและ Roadmap](#ข้อจำกัดและ-roadmap)
- [English](#english)
- [Security](#security)
- [Contributing](#contributing)

# ภาษาไทย

## SockBoi Agent คืออะไร

SockBoi Agent คือ **Control Plane สำหรับงาน Security Assessment ที่ได้รับอนุญาต** ไม่ใช่เครื่องมือโจมตีอัตโนมัติแบบ unrestricted จุดประสงค์คือช่วยเปลี่ยนคำขอประเมินความปลอดภัยให้เป็นแผนงานที่ตรวจสอบได้ โดยมีขอบเขตและสิทธิ์ที่ชัดเจนตั้งแต่ต้นจนจบ

แนวคิดสำคัญคือแยกหน้าที่ระหว่าง:

1. **AI / Agent** — ช่วยทำความเข้าใจคำขอ เสนอแผน จัดหมวดหมู่ความเสี่ยง และสรุปผล
2. **Policy Engine** — ตรวจสอบ Scope และเงื่อนไขการอนุญาตด้วยกฎที่กำหนดแน่นอน ไม่ให้ AI เปลี่ยนกฎเอง
3. **Human Approval** — ผู้มีสิทธิ์ตรวจสอบและอนุมัติ Action ที่มีความเสี่ยงก่อนนำไปใช้
4. **Execution Adapter** — ส่วนเชื่อมต่อเครื่องมือภายนอกที่ต้องถูกจำกัดสิทธิ์และผ่าน Policy Gate (ยังไม่เปิดใช้งานในรุ่นนี้)

**หลักการ:** AI เสนอได้ แต่ไม่มีสิทธิ์อนุมัติตัวเองหรือข้าม Scope/Policy

## ความสามารถที่มีในโค้ดปัจจุบัน

| ส่วนประกอบ | สถานะ | รายละเอียด |
|---|---|---|
| Assessment Planner | มี | สร้างแผนประเมินจาก Engagement และ Target ที่อยู่ใน Scope |
| Engagement Management | มี | สร้าง/อ่าน Engagement พร้อม Authorization Reference และ Asset Scope |
| Scope Validation | มี | ตรวจ Target เทียบกับ Asset ที่ได้รับอนุญาต |
| API Key Authentication | มี | Bearer API key ตรวจสอบกับ SHA-256 digest ที่ตั้งค่าฝั่ง Server |
| RBAC | มี | แยกสิทธิ์ตาม role เช่น admin, operator และ reviewer ใน endpoint ที่กำหนด |
| Tenant Isolation | มี | ผูก Engagement กับ tenant จาก Principal และป้องกันการอ่านข้าม tenant |
| SQLAlchemy Store | มี | จัดเก็บ Engagement, Approval, Finding และ Audit Event ผ่าน SQLAlchemy |
| Action-bound Approval | มี | ผูก Approval กับ Engagement, Tenant, Target, Adapter, Technique, Parameters และ Risk ด้วย SHA-256 digest |
| One-time Approval Consume | มี | ตรวจ digest, สถานะ, อายุอนุมัติ และป้องกันการ consume ซ้ำด้วย database conditional update |
| Knowledge Ingestion | มี | นำเข้า Markdown และค้นหาด้วยคำสำคัญ |
| Typed Tool Registry | มี | แสดงรายการเครื่องมือและ schema; ปิดการ execute |
| Findings | มี | บันทึก Finding ที่ผูกกับ Engagement และตรวจ Scope |
| Audit Events | มี | บันทึกเหตุการณ์สำคัญของระบบ |
| Evidence Hash | มี | คำนวณ SHA-256 โดยไม่เก็บเนื้อหาหลักฐาน |
| Hash-chain Audit Integration | ยังไม่มี | มี primitive/helper แต่ยังไม่เชื่อมเข้ากับวงจรจัดเก็บ Audit ของ API |
| LLM Runtime | ยังไม่มี | ยังไม่มีการเชื่อม Provider เพื่อให้ LLM ทำงานใน API flow |
| MCP Runtime / Scanner Execution | ยังไม่มี | ยังไม่มีการเรียก MCP Server, Nmap, ZAP หรือ Scanner จริง |

### Approval ทำงานอย่างไร

Approval ไม่ได้อนุมัติแบบกว้าง ๆ แต่ผูกกับ Action Envelope ที่ประกอบด้วย:

- Engagement ID และ Tenant ID
- Target
- Adapter ID และ Technique ID
- Parameters
- Risk level

ระบบคำนวณ SHA-256 digest จากข้อมูลเหล่านี้ เมื่อขอใช้ Approval ต้องส่ง Envelope ที่ตรงกับต้นฉบับทุกส่วน การเปลี่ยน Target, Technique, Adapter หรือ Parameters จะทำให้ digest ไม่ตรงและถูกปฏิเสธ

Approval ที่อนุมัติแล้วมีอายุ **15 นาที** และ consume ได้ครั้งเดียว ผู้ร้องขอไม่สามารถอนุมัติคำขอของตัวเองได้ การเรียก `/approvals/{id}/consume` เป็นเพียงการใช้สิทธิ์อนุมัติ ไม่ได้ส่งคำขอเครือข่ายหรือรันเครื่องมือใด ๆ

## สถาปัตยกรรม

```mermaid
flowchart TD
    U[User / Security Analyst] --> API[FastAPI]
    API --> AUTH[API Key Authentication]
    AUTH --> RBAC[RBAC + Tenant Boundary]
    RBAC --> ENG[Engagement + Scope]
    ENG --> PLAN[Assessment Planner]
    PLAN --> POLICY[Deterministic Policy Engine]
    POLICY --> APPROVAL[Human Approval Gate]
    APPROVAL --> CATALOG[Typed Tool Registry]
    CATALOG -. execution disabled .-> ADAPTER[Future Isolated Adapter]
    API --> DB[(SQLAlchemy Database)]
    API --> AUDIT[Audit Events]
    KNOW[Untrusted Knowledge / Skills] --> PLAN
```

### ส่วนประกอบหลัก

- **Agent Core:** ประสานงานและสร้างแผนการประเมิน ปัจจุบัน Planner เป็น logic ในแอป ไม่ใช่ LLM agent runtime ที่เชื่อมโมเดลภายนอก
- **Skills / Knowledge:** เก็บ playbook และเอกสารอ้างอิง Markdown เนื้อหาที่นำเข้าถือเป็น Untrusted Input เสมอ
- **MCP / Tool Registry:** ระบุเครื่องมือและ input schema ที่ระบบรู้จัก ปัจจุบันเป็น Catalog เท่านั้น
- **Policy Layer:** ตรวจ Scope, Risk และ Approval โดยไม่เชื่อคำสั่งจาก Knowledge หรือ Model Output
- **Storage:** SQLAlchemy ใช้กับข้อมูลหลักของ Engagement, Approval, Finding และ Audit Event; การตั้งค่า schema ปัจจุบันใช้ `create_all` ยังไม่มี Alembic migration workflow

ดูรายละเอียดเพิ่มเติม: [Agent](agent/README.md) · [Skills](skills/README.md) · [MCP](mcp/README.md) · [Architecture](docs/architecture.md) · [Roadmap](docs/roadmap.md)

## ติดตั้งและเริ่มใช้งาน

### ความต้องการ

- Python **3.12 หรือใหม่กว่า**
- pip
- Git
- ฐานข้อมูลที่ SQLAlchemy รองรับ (SQLite เหมาะกับการทดลอง; PostgreSQL เหมาะกับการพัฒนาแบบหลายผู้ใช้)

### 1. Clone Repository

```bash
git clone https://github.com/SockBoi-Hook-Patch/SockBoi-Agent.git
cd SockBoi-Agent
git checkout feat/v0.4-active-assessment-foundation
```

หากต้องการใช้ branch หลัก ให้ตัดคำสั่ง checkout ออก แต่ความสามารถอาจต่างจาก branch ที่ระบุในเอกสารนี้

### 2. สร้าง Virtual Environment

Linux / macOS:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. ติดตั้ง Dependencies

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### 4. ตั้งค่า API Key

API ทุก endpoint ยกเว้น `GET /health` ต้องมี Bearer API key ที่ถูกต้อง หากยังไม่ตั้งค่า Keyring ระบบจะ fail closed และตอบกลับว่า Authentication ยังไม่ได้ตั้งค่า

ดูวิธีสร้าง Keyring ในหัวข้อ [ตั้งค่า API Authentication](#ตั้งค่า-api-authentication)

### 5. เริ่ม API Server

```bash
uvicorn sockboi.main:app --reload
```

เปิดเอกสาร API แบบ Interactive ได้ที่:

- Swagger UI: http://127.0.0.1:8000/docs
- Health Check: http://127.0.0.1:8000/health

> ใช้ `--reload` เฉพาะเครื่องพัฒนาเท่านั้น อย่าเปิด Development Server ออกอินเทอร์เน็ต

## ตั้งค่า API Authentication

ระบบอ่านตัวแปรแวดล้อม `SOCKBOI_API_KEYS` เป็น JSON Array แต่ละรายการต้องมี:

- `key_sha256`: SHA-256 hex digest ของ API key จริง
- `subject`: ชื่อ Principal/ผู้ใช้งาน
- `tenant_id`: Tenant ที่ผู้ใช้งานสังกัด
- `roles`: Array ของ role

### สร้าง API Key และ Digest

ตัวอย่างสร้าง Key แบบสุ่มและคำนวณ digest ด้วย Python:

```bash
python -c "import secrets,hashlib; k=secrets.token_urlsafe(32); print('API_KEY='+k); print('KEY_SHA256='+hashlib.sha256(k.encode()).hexdigest())"
```

เก็บค่า `API_KEY` ไว้เป็นความลับ และนำเฉพาะค่า `KEY_SHA256` ไปใส่ใน Keyring ตัวอย่างด้านล่างใช้ค่า placeholder ต้องแทนด้วย digest จริง:

```json
[
  {
    "key_sha256": "<64-character-lowercase-sha256-hex>",
    "subject": "security-operator",
    "tenant_id": "tenant-lab",
    "roles": ["operator"]
  },
  {
    "key_sha256": "<another-64-character-sha256-hex>",
    "subject": "security-reviewer",
    "tenant_id": "tenant-lab",
    "roles": ["reviewer"]
  }
]
```

ตั้งค่า Environment Variable ก่อนเปิด Server

Linux / macOS:

```bash
export SOCKBOI_API_KEYS='[{"key_sha256":"<OPERATOR_SHA256>","subject":"security-operator","tenant_id":"tenant-lab","roles":["operator"]},{"key_sha256":"<REVIEWER_SHA256>","subject":"security-reviewer","tenant_id":"tenant-lab","roles":["reviewer"]}]'
```

Windows PowerShell:

```powershell
$env:SOCKBOI_API_KEYS='[{"key_sha256":"<OPERATOR_SHA256>","subject":"security-operator","tenant_id":"tenant-lab","roles":["operator"]},{"key_sha256":"<REVIEWER_SHA256>","subject":"security-reviewer","tenant_id":"tenant-lab","roles":["reviewer"]}]'
```

เรียก API โดยใช้ **API key จริง** ไม่ใช่ digest:

```bash
curl http://127.0.0.1:8000/engagements \
  -H "Authorization: Bearer YOUR_OPERATOR_API_KEY"
```

### Roles ที่ใช้งานใน API

| Role | สิทธิ์โดยสรุป |
|---|---|
| `admin` | สิทธิ์ระดับผู้ดูแลใน endpoint ที่รองรับ |
| `operator` | สร้าง Engagement, ขอ Approval และสร้าง Finding |
| `reviewer` | ตัดสินคำขอ Approval |
| role อื่น | อ่านได้เฉพาะ endpoint ที่ไม่กำหนด role เพิ่ม แต่ยังต้องผ่าน Authentication และ Tenant Boundary |

สิทธิ์จริงถูกกำหนดที่แต่ละ endpoint ไม่ควรตีความตารางนี้ว่าเป็น Permission Matrix ที่ครอบคลุมทุกกรณี

**อย่า commit API key จริง, .env, digest ที่ไม่ควรเปิดเผย, หรือข้อมูลลูกค้าลง Git**

## Workflow การใช้งาน

1. **เตรียม Authorization:** ยืนยันว่ามีหนังสืออนุญาตหรือหลักฐานสิทธิ์ตรวจสอบ และกำหนดช่วงเวลา/ข้อจำกัดของงาน
2. **สร้าง Engagement:** ใส่ Authorization Reference และ Asset Scope ให้ชัดเจน
3. **สร้าง Assessment Plan:** ส่ง Engagement ID และ Target ที่อยู่ใน Scope ให้ Planner
4. **ทบทวนแผน:** ตรวจ Target, เทคนิค, ความเสี่ยง และผลกระทบที่อาจเกิดขึ้น
5. **ขอ Approval:** ส่ง Action ที่ระบุ Target, Adapter, Technique, Parameters และ Risk
6. **ให้ Reviewer ตัดสิน:** Reviewer ต้องเป็น Principal แยกจากผู้ร้องขอ
7. **ตรวจ Policy / Consume Approval:** ตรวจว่าข้อมูล Action ตรงกับที่อนุมัติและยังไม่หมดอายุ
8. **บันทึก Finding และ Audit:** จัดเก็บผลที่ตรวจพบ พร้อมแยกข้อเท็จจริงออกจากข้อสันนิษฐาน

> ในรุ่นปัจจุบัน Workflow นี้เป็นการจัดการแผน สิทธิ์ และข้อมูลผ่าน API เท่านั้น การ Consume Approval ไม่ได้ execute Active Check

## ตัวอย่าง Prompt สำหรับ AI

Prompt เหล่านี้เป็น **ตัวอย่างแนวทางการสั่ง AI ภายนอกหรือผู้ช่วยนักวิเคราะห์** ไม่ใช่คำสั่งที่ระบบมี LLM Runtime รับไป execute อัตโนมัติในตอนนี้ ควรให้ AI สร้างผลลัพธ์ที่มนุษย์ตรวจสอบได้ และส่งข้อมูลเข้า API ผ่านขั้นตอนที่กำหนด

### 1. วางแผนประเมินแบบ Passive

```text
คุณคือผู้ช่วยวางแผน Security Assessment

เป้าหมาย: [ระบุ Domain / IP / Asset]
Engagement ID: [ระบุ ID]
ขอบเขตที่ได้รับอนุญาต: [วาง Scope ที่ยืนยันแล้ว]
ข้อจำกัด: Passive assessment เท่านั้น ห้ามส่งคำขอทดสอบไปยังเป้าหมาย

งานที่ต้องทำ:
1. สรุปขอบเขตและข้อจำกัด
2. เสนอรายการตรวจสอบจากข้อมูลที่ให้มาเท่านั้น
3. จัดลำดับตามความเสี่ยงและความสำคัญ
4. ระบุข้อมูลที่ยังขาดและสิ่งที่ต้องขออนุญาตเพิ่ม
5. แยกข้อเท็จจริง สมมติฐาน และข้อเสนอแนะ
6. ห้ามแต่งผลการตรวจหรืออ้างว่าทดสอบแล้ว

ส่งผลลัพธ์เป็น JSON:
{
  "scope_summary": "...",
  "assumptions": [],
  "checks": [
    {
      "name": "...",
      "target": "...",
      "technique": "...",
      "risk": "passive",
      "evidence_required": [],
      "approval_required": false
    }
  ],
  "out_of_scope": [],
  "open_questions": []
}
```

### 2. เสนอแผน Active HTTP Inspection (ยังไม่ execute)

```text
ช่วยออกแบบแผนตรวจสอบ HTTP Security Configuration สำหรับ Asset
ที่อยู่ใน Engagement Scope และได้รับอนุญาตอย่างชัดเจนเท่านั้น

ข้อกำหนด:
- เสนอเฉพาะ HTTP GET แบบ read-only
- ห้าม POST, PUT, PATCH, DELETE
- ห้าม brute force, fuzzing, DoS หรือ exploit
- ห้ามตาม Redirect ไปยัง Host อื่นโดยอัตโนมัติ
- ระบุ Target, Adapter ID, Technique ID และ Parameters ให้ชัด
- ระบุเหตุผลและ Risk ของแต่ละ Action
- ระบุ Approval ที่ต้องได้รับก่อนทำงาน
- ถ้า Scope ไม่ชัดเจน ให้หยุดและถาม ไม่เดาเอง

สำคัญ: ตอนนี้ให้สร้างแผนและ Action Schema เท่านั้น
ห้ามอ้างว่าได้ส่ง HTTP Request หรือพบช่องโหว่แล้ว
```

### 3. วิเคราะห์ Findings และจัดทำรายงาน

```text
คุณคือ Security Analyst

วิเคราะห์ Findings และ Evidence ที่แนบมา โดย:
1. จัดกลุ่มตาม Asset และประเภทช่องโหว่
2. ประเมิน Severity พร้อมเหตุผล
3. อธิบายผลกระทบทางธุรกิจและ Technical Impact
4. เสนอแนวทางแก้ไขที่ตรวจสอบได้
5. ระบุ Evidence ที่รองรับแต่ละข้อ
6. แยก Confirmed Finding, Potential Finding และ False Positive
7. ห้ามสร้าง Evidence, URL, CVE หรือผลการทดสอบขึ้นเอง
8. ถ้าข้อมูลไม่พอ ให้ระบุว่า "ยังยืนยันไม่ได้"

รูปแบบรายงาน:
- Executive Summary
- Scope and Methodology
- Findings by Severity
- Evidence
- Remediation
- Limitations
- Retest Recommendations
```

### 4. ตรวจสอบ Scope และ Approval ก่อนเสนอ Action

```text
ตรวจ Action Schema ต่อไปนี้ก่อนส่งให้ผู้ตรวจสอบ:

[วาง Action Schema]

ตรวจว่า:
- Target อยู่ใน Engagement Scope หรือไม่
- Action มีความเสี่ยงระดับใด
- มี Adapter และ Technique ที่ระบุชัดหรือไม่
- Parameters มีความจำเป็นและจำกัดขอบเขตหรือไม่
- ต้องใช้ Human Approval หรือไม่
- มีความเสี่ยงต่อข้อมูลหรือความพร้อมใช้งานหรือไม่

หากข้อมูลใดไม่ชัดเจน ให้ปฏิเสธการเสนอ Action และอธิบายเหตุผล
ห้ามลดระดับ Risk เพื่อให้ผ่าน Approval
```

### หลักการเขียน Prompt ให้ปลอดภัย

- ระบุ Engagement และ Scope ที่ได้รับอนุญาตทุกครั้ง
- ระบุว่าให้ทำ Planning, Analysis หรือ Execution (เมื่อมีระบบรองรับ) ให้ชัด
- ระบุข้อห้ามและข้อจำกัดด้านผลกระทบ
- บังคับให้ AI แยก Evidence ออกจาก Assumption
- ให้ AI ส่ง Structured Output ที่ตรวจสอบได้
- อย่าใส่ Secret, API Key หรือข้อมูลส่วนบุคคลลงใน Prompt โดยไม่จำเป็น

## API Endpoints

API ต้องใช้ Header `Authorization: Bearer <API_KEY>` ทุก endpoint ยกเว้น `GET /health`

| Method | Endpoint | หน้าที่ |
|---|---|---|
| GET | `/health` | Health check และเวอร์ชัน |
| POST | `/engagements` | สร้าง Engagement (admin/operator) |
| GET | `/engagements` | แสดง Engagement ใน Tenant ของผู้เรียก |
| GET | `/engagements/{id}` | อ่าน Engagement ที่เข้าถึงได้ |
| POST | `/engagements/{id}/plan?target=...` | สร้าง Assessment Plan |
| POST | `/engagements/{id}/approvals` | ขอ Action-bound Approval (admin/operator) |
| POST | `/approvals/{id}/decide?approved=true` | อนุมัติ/ปฏิเสธ (admin/reviewer) |
| POST | `/approvals/{id}/consume?engagement_id=...` | Consume Approval แบบ one-time; ไม่ execute Action |
| POST | `/policy/check` | ตรวจ Scope, Risk และ Approval |
| POST | `/findings` | สร้าง Finding (admin/operator) |
| GET | `/engagements/{id}/audit` | อ่าน Audit Events ของ Engagement |
| POST | `/knowledge/ingest` | นำเข้า Markdown เป็น Untrusted Knowledge |
| GET | `/knowledge/search?query=...` | ค้นหา Knowledge |
| GET | `/tools` | ดู Typed Tool Catalog (execution disabled) |
| POST | `/evidence/hash` | คำนวณ SHA-256 โดยไม่บันทึก Content |

ดู Request/Response Schema แบบเต็มและทดลองเรียกได้ที่ Swagger UI: `/docs`

## ข้อจำกัดและ Roadmap

### สิ่งที่ยังไม่มี / ห้ามเข้าใจว่าทำได้แล้ว

- ไม่มี LLM Provider หรือ Prompt-to-Action Runtime ที่เชื่อมใน API
- ไม่มีการ execute Nmap, Nuclei, ZAP, Browser หรือ MCP tools
- ไม่มี Active HTTP Inspection Adapter ที่ทำงานจริง
- Approval Consume เป็นการใช้สิทธิ์ ไม่ใช่การรัน Network Action
- Hash-chain Audit helper ยังไม่ถูกเชื่อมเข้ากับ API/Storage Lifecycle; Audit Events ปัจจุบันยังไม่ใช่หลักฐานแบบ tamper-evident
- Database schema ใช้ SQLAlchemy `create_all`; ยังไม่มี Alembic migration workflow
- ยังต้องทบทวน hardening เช่น approval decision immutability/revocation, actor binding สำหรับการ consume, parameter schema allowlist และการทดสอบขอบเขตเพิ่มเติม
- ยังไม่ผ่านการรับรอง Production Security Review

### Roadmap

| ระยะ | เป้าหมาย |
|---|---|
| v0.4 | Authentication, RBAC, Tenant Isolation, Durable Store, Action-bound Approval และ API foundation |
| v0.5 | Isolated Worker และ HTTP GET-only security configuration inspection พร้อม DNS pinning, redirect controls, SSRF protection, egress allowlist, timeout และ rate limit |
| v0.6 | Versioned Skills, provenance, safe ingestion และ prompt-injection isolation |
| v0.7 | MCP Runtime แบบ typed allowlist พร้อม Policy Gate, timeout และ cancellation |
| v0.8 | LLM orchestration, structured output และ evaluation suite โดย Policy Engine ยังคงเป็นผู้ตัดสินสิทธิ์ |

รายการใน Roadmap คือแผนพัฒนา ไม่ใช่ความสามารถที่เปิดใช้งานแล้ว ดู [docs/roadmap.md](docs/roadmap.md)

---

# English

## Overview

SockBoi Agent is a **policy-first control plane for authorized security assessments**. It helps security teams define engagements, validate asset scope, create assessment plans, manage human approvals, record findings, and maintain operational audit events.

It is not an unrestricted exploitation framework. The deterministic Policy Engine remains the authorization authority; AI-generated plans and imported knowledge are untrusted inputs.

## Current capabilities

- FastAPI service with Bearer API-key authentication (SHA-256 digests stored in server configuration).
- Role-based access checks for selected operations.
- Tenant-scoped engagement access; tenant identity is derived from the authenticated principal.
- SQLAlchemy-backed records for engagements, approvals, findings, and audit events.
- Scope-aware assessment planning.
- Action-bound approval digests covering engagement, tenant, target, adapter, technique, parameters, and risk.
- One-time approval consumption with expiry and database conditional update; consumption does not execute the approved action.
- Markdown knowledge ingestion and keyword search; imported content is untrusted reference data.
- Typed tool catalogue with execution disabled.
- Finding management, audit event retrieval, and SHA-256 evidence digest calculation without content persistence.

## Quick start

Requires Python 3.12+.

```bash
git clone https://github.com/SockBoi-Hook-Patch/SockBoi-Agent.git
cd SockBoi-Agent
git checkout feat/v0.4-active-assessment-foundation
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Configure `SOCKBOI_API_KEYS` as a JSON array containing `key_sha256`, `subject`, `tenant_id`, and `roles`. See the Thai authentication section above for key generation and configuration examples.

Start the API:

```bash
uvicorn sockboi.main:app --reload
```

Open http://127.0.0.1:8000/docs. Only `GET /health` is exempt from API-key authentication.

## Example AI prompts

Prompts are guidance for an external AI assistant or analyst; this repository does not currently provide an integrated LLM runtime.

- **Passive planning:** provide the authorized asset scope, request a structured checklist, and prohibit active requests or invented evidence.
- **Active HTTP plan (planning only):** request a bounded GET-only inspection plan with explicit target, adapter, technique, parameters, risk, and approval requirements. Do not claim execution.
- **Findings report:** classify supplied findings, explain impact and remediation, cite supplied evidence, and label uncertain conclusions as unconfirmed.
- **Policy review:** inspect an Action Schema for scope, risk, parameter minimization, and required human approval.

## Important limitations

No LLM runtime, MCP execution, scanner integration, browser automation, or live network assessment adapter is enabled. Approval consumption is authorization bookkeeping only. Hash-chain audit helpers are not yet integrated into the API lifecycle, and database migrations are not yet managed by Alembic. This is a Developer Preview, not a production-ready pentest runner.

See [Architecture](docs/architecture.md), [Agent System](docs/agent-system.md), [Roadmap](docs/roadmap.md), and [SECURITY.md](SECURITY.md).

---

## Security

SockBoi Agent is intended only for assets for which you have explicit authorization.

- Define engagement scope before assessment.
- Keep API keys secret and use separate principals for operators and reviewers.
- Require human approval for active or state-changing operations.
- Treat LLM output, Skills, Markdown, and external content as untrusted.
- Do not add arbitrary shell execution, credential theft, persistence, denial-of-service, or out-of-scope actions.
- Do not expose the development server to public networks.
- Do not use this preview as a production security control or as proof that a target is secure.

Report vulnerabilities through the process described in [SECURITY.md](SECURITY.md).

## Contributing

Contributions should include tests and documentation, preserve explicit scope enforcement, and keep authorization decisions outside model-generated content. Review [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a pull request.

## AI-assisted development

Parts of the documentation and development workflow were prepared with assistance from ChatGPT (OpenAI) and OpenAI Codex. These tools are acknowledged as AI assistance, not as repository owners or GitHub contributors.


### Audit integrity note

Audit events are now persisted with a SHA-256 hash-chain record and can be checked through the reviewer/admin-only `GET /engagements/{engagement_id}/audit/verify` endpoint. The verification currently checks the complete shared audit stream, including sequence continuity and event payload hashes. A valid chain is tamper-evident, not independently tamper-proof: production deployments should periodically anchor the reported head hash in a separately controlled system (for example, signed external checkpoints or write-once storage). Database-level concurrent writers across multiple application processes and schema migration management remain deployment-hardening work; this foundation does not claim to provide external anchoring or a complete immutable-storage guarantee.


The audit verification endpoint requires an authenticated principal with the `reviewer` or `admin` role and a tenant-owned engagement identifier.


Verification reports the chain validity, number of chained audit events, and current head digest; it does not repair or rewrite a damaged chain.
