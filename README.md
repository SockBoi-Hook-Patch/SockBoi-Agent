# SockBoi Agent

**Policy-first AI Security Assessment Platform**  
แพลตฟอร์มสำหรับวางแผนและจัดการ Security Assessment ในระบบที่ได้รับอนุญาต โดยยึด Scope, Deterministic Policy, Human Approval และ Auditability เป็นหลัก

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/) [![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)](https://fastapi.tiangolo.com/) [![Security](https://img.shields.io/badge/Design-Policy--First-informational)](SECURITY.md)

> **สถานะ ณ 2 พฤศจิกายน 2026: Developer Preview — package version 0.4.0**
>
> `main` มี security foundation และ APK static ZIP inspection endpoint แล้ว ส่วน ADB/Frida runtime, APK decompilation, patch generation, live bypass testing, scanner execution, MCP runtime และ LLM orchestration ยังไม่ใช่ความสามารถที่เปิดใช้งานจริง
>
> Version ใน `pyproject.toml` คือ `0.4.0` การ Merge PR ไม่ได้สร้าง release/tag ให้อัตโนมัติ

---

## Contents

- [ภาษาไทย](#ภาษาไทย)
- [English](#english)
- [Security model](#security-model)
- [Roadmap](docs/roadmap.md)
- [Architecture](docs/architecture.md)
- [Android APK roadmap](docs/apk-reverse-engineering-roadmap.md)
- [Contributing](CONTRIBUTING.md)

# ภาษาไทย

## SockBoi Agent คืออะไร

SockBoi Agent คือ **Control Plane สำหรับ Security Assessment ที่ได้รับอนุญาต** ช่วยจัดการ Engagement, Asset Scope, Assessment Plan, Approval, Findings และ Audit Evidence โดยออกแบบให้ AI หรือ Skill ไม่สามารถอนุมัติ Action หรือขยายขอบเขตเองได้

องค์ประกอบหลัก:

1. **Agent / Planner** — ช่วยจัดโครงสร้างแผนและข้อเสนอการตรวจสอบ ปัจจุบันยังไม่มี integrated LLM runtime
2. **Policy Engine** — ตรวจ Scope, Risk และเงื่อนไขการอนุญาต
3. **Human Approval** — ผู้มีสิทธิ์ตรวจสอบ Action ก่อนดำเนินการที่มีความเสี่ยง
4. **Tool Registry / Adapters** — เก็บ typed tool definitions; live execution adapters ยังไม่เปิดใช้งาน
5. **Evidence / Audit** — บันทึกผลและตรวจสอบความถูกต้องของ Audit Chain

## สถานะความสามารถใน `main`

| ความสามารถ | สถานะ | ขอบเขตปัจจุบัน |
|---|---|---|
| FastAPI service | Implemented | API service และ health endpoint |
| API-key authentication | Implemented | Bearer key ตรวจจาก SHA-256 digest ฝั่ง Server; fail-closed |
| RBAC | Implemented | Role checks ใน endpoint ที่กำหนด |
| Tenant isolation | Implemented | Principal-bound tenant สำหรับ Engagement และ Knowledge; APK inspect ตรวจ tenant ผ่าน Engagement |
| Engagement / Scope | Implemented | สร้างและอ่าน Engagement พร้อม asset scope |
| Assessment Planner | Implemented | สร้างแผนจาก Engagement และ target ใน scope; ไม่ใช่ LLM agent |
| Action-bound Approval | Implemented | ผูก approval กับ Engagement, Tenant, Target, Adapter, Technique, Parameters และ Risk |
| One-time approval consume | Implemented | ตรวจ envelope/expiry และป้องกัน consume ซ้ำ; ไม่ได้ execute action |
| SQLAlchemy persistence | Implemented | จัดเก็บ Engagement, Approval, Finding และ Audit Event; ยังใช้ `create_all` |
| Audit hash chain | Implemented | Engagement-scoped verification และ HMAC checkpoint export |
| Markdown Knowledge | Implemented | Tenant-scoped ingestion และ keyword search; เนื้อหาเป็น untrusted input |
| Typed Tool Catalog | Implemented | แสดง tool/schema แต่ execution ถูกปิด |
| Findings / Evidence hash | Implemented | จัดเก็บ Finding และคำนวณ SHA-256 digest โดยไม่เก็บ evidence content ผ่าน hash endpoint |
| APK static inspection | Implemented | Upload APK แบบ bounded; ZIP safety checks, SHA-256, DEX/native/resource inventory และ parse plain-text XML manifest |
| APK patch comparison | Planned / PR review | ยังไม่อยู่ใน `main`; byte-level archive diff และ patch audit อยู่ระหว่างพัฒนา |
| JADX / Apktool / binary manifest | Planned | ยังไม่มี decompilation หรือ binary XML decoder |
| APK signer verification | Planned | การพบ META-INF signature files ไม่ใช่การยืนยันลายเซ็นเชิงคริปโต |
| ADB / Emulator Manager | Skill / Design only | ยังไม่มี live ADB adapter หรือ disposable emulator manager |
| Frida / Runtime Hook | Skill / Template only | ยังไม่มี live Frida runtime; ตัวอย่าง hook ไม่ได้ถูกรันโดย API |
| Protection resilience / bypass audit | Design / Lab workflow | ยังไม่มี automated runtime test harness |
| Patch generation / APK repackaging | Not implemented | ไม่มีระบบแก้ไข/repackage/re-sign APK |
| LLM / MCP / Scanner execution | Not implemented | ไม่มี integrated LLM, MCP client หรือ Nmap/ZAP/Browser execution |

**ข้อควรเข้าใจ:** การมี Skill, playbook, script template หรือ roadmap ไม่ได้หมายความว่า Agent เรียกใช้เครื่องมือนั้นได้จริง ต้องมี adapter, worker isolation, tests และ CI ผ่านก่อนจึงนับเป็น executable capability

## APK Static Inspection API

Endpoint:

`POST /engagements/{engagement_id}/apk/inspect`

- Authentication: Bearer API key
- Required role: `admin` หรือ `operator`
- Multipart field: `file`
- ตรวจว่าเป็น ZIP-based APK และบังคับ size/archive safety limits
- คำนวณ SHA-256 และแสดงขนาด/จำนวน archive entries
- แสดงรายการ DEX, native libraries, resources และ assets
- อ่าน Manifest ได้เฉพาะกรณีเป็น plain-text XML; binary Android XML จะระบุว่าไม่รองรับการ decode
- บันทึก audit event ที่ผูกกับ Engagement
- ไม่ extract ไฟล์ลง disk, ไม่เก็บ APK ต้นฉบับ และไม่ execute app code

ตัวอย่าง:

```bash
curl -X POST "http://127.0.0.1:8000/engagements/<ENGAGEMENT_ID>/apk/inspect" \
  -H "Authorization: Bearer <OPERATOR_API_KEY>" \
  -F "file=@./sample.apk"
```

ใช้เฉพาะ APK ที่ได้รับอนุญาตให้ตรวจสอบ และอย่าอัปโหลด APK ที่มีข้อมูลลับหรือข้อมูลส่วนบุคคลโดยไม่มีฐานสิทธิ์และมาตรการจัดการข้อมูลที่เหมาะสม

## Architecture

```text
User / Analyst
      |
FastAPI + API-key Authentication
      |
RBAC + Tenant Boundary
      |
Engagement + Asset Scope
      |
Assessment Planner
      |
Deterministic Policy + Human Approval
      |
Typed Tool Catalog (execution disabled)
      |
Future isolated workers / adapters

SQLAlchemy Store ---- Audit Hash Chain
Knowledge / Skills -- untrusted reference input
APK upload ---------- bounded static ZIP inspection
```

ดูเอกสาร: [Architecture](docs/architecture.md) · [Agent](agent/README.md) · [Skills](skills/README.md) · [MCP](mcp/README.md) · [Roadmap](docs/roadmap.md)

## ติดตั้งและเริ่มใช้งาน

### Requirements

- Python 3.12+
- pip และ Git
- SQLite สำหรับทดลอง หรือ PostgreSQL สำหรับการพัฒนาแบบหลายผู้ใช้

### 1. Clone และติดตั้ง

```bash
git clone https://github.com/SockBoi-Hook-Patch/SockBoi-Agent.git
cd SockBoi-Agent
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Windows PowerShell:

```powershell
git clone https://github.com/SockBoi-Hook-Patch/SockBoi-Agent.git
cd SockBoi-Agent
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### 2. ตั้งค่า API Authentication

ระบบอ่าน `SOCKBOI_API_KEYS` เป็น JSON array โดยแต่ละ principal ต้องมี `key_sha256`, `subject`, `tenant_id` และ `roles` ระบบไม่เก็บ API key แบบ plaintext ใน keyring

สร้าง key และ digest:

```bash
python -c "import secrets,hashlib; k=secrets.token_urlsafe(32); print('API_KEY='+k); print('KEY_SHA256='+hashlib.sha256(k.encode()).hexdigest())"
```

ตั้งค่า Environment Variable โดยแทน placeholder ด้วย digest จริง:

```bash
export SOCKBOI_API_KEYS='[{"key_sha256":"<OPERATOR_SHA256>","subject":"security-operator","tenant_id":"tenant-lab","roles":["operator"]},{"key_sha256":"<REVIEWER_SHA256>","subject":"security-reviewer","tenant_id":"tenant-lab","roles":["reviewer"]}]'
```

สำหรับ Audit Checkpoint ให้ตั้ง `SOCKBOI_AUDIT_CHECKPOINT_KEY` เป็น secret แยกต่างหากและเก็บไว้นอก Git/Database

### 3. เริ่ม API

```bash
uvicorn sockboi.main:app --reload
```

- Swagger UI: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

ทุก endpoint ยกเว้น `GET /health` ต้องมี Bearer API key ที่ถูกต้อง ใช้ `--reload` เฉพาะ local development เท่านั้น

### Docker Compose

```bash
cp .env.example .env
# ตั้ง POSTGRES_PASSWORD และ SOCKBOI_API_KEYS ใน .env
docker compose up --build -d
docker compose logs -f api
```

ห้าม commit `.env`, API keys, checkpoint secrets หรือข้อมูลลูกค้าลง Git

## Approval model

Approval เป็น Action-bound ไม่ใช่ blanket approval โดยผูกกับ:

- Engagement ID และ Tenant ID
- Target
- Adapter ID และ Technique ID
- Parameters
- Risk level

Approval ที่อนุมัติแล้วมีอายุ 15 นาทีและ consume ได้ครั้งเดียว ผู้ร้องขอไม่สามารถอนุมัติคำขอของตัวเองได้ การ consume เป็นเพียงการบันทึก/ตรวจสิทธิ์ ไม่ได้เรียก network หรือรันเครื่องมือ

## API endpoints

| Method | Endpoint | รายละเอียด |
|---|---|---|
| GET | `/health` | Health check และ version |
| POST | `/engagements` | สร้าง Engagement |
| GET | `/engagements` | อ่าน Engagement ใน Tenant |
| GET | `/engagements/{id}` | อ่าน Engagement |
| POST | `/engagements/{id}/plan` | สร้าง Assessment Plan |
| POST | `/engagements/{id}/approvals` | ขอ Action-bound Approval |
| POST | `/approvals/{id}/decide` | Reviewer ตัดสิน Approval |
| POST | `/approvals/{id}/consume` | Consume Approval; ไม่ execute |
| POST | `/policy/check` | ตรวจ Scope / Risk / Approval |
| POST | `/findings` | บันทึก Finding |
| GET | `/engagements/{id}/audit` | อ่าน Audit Events |
| GET | `/engagements/{id}/audit/verify` | ตรวจ Audit Chain |
| GET | `/engagements/{id}/audit/checkpoint` | สร้าง HMAC checkpoint |
| POST | `/knowledge/ingest` | นำเข้า Markdown |
| GET | `/knowledge/search` | ค้นหา Knowledge |
| GET | `/tools` | ดู Typed Tool Catalog |
| POST | `/evidence/hash` | คำนวณ SHA-256 |
| POST | `/engagements/{id}/apk/inspect` | ตรวจ APK แบบ static ZIP inventory |

Request/response schema ที่แน่นอนให้ดู Swagger UI ที่ `/docs`

## Roadmap

ดู [docs/roadmap.md](docs/roadmap.md) สำหรับ milestone และสถานะล่าสุด ภาพรวมลำดับงาน Android:

1. APK static intake และ ZIP inspection — อยู่ใน main
2. Read-only APK comparison และ patch provenance — อยู่ระหว่าง PR/review
3. Binary manifest, DEX, resource, native และ signer analysis providers
4. Isolated Android worker, disposable emulator และ typed ADB adapter
5. Frida reviewed-template runtime, observation hooks และ evidence pipeline
6. Lab-only protection resilience tests และ report correlation

---

# English

## Overview

SockBoi Agent is a **policy-first control plane for authorized security assessments**. It manages engagements, asset scope, assessment plans, approvals, findings, and audit evidence. AI output and imported Skills are untrusted; authorization remains deterministic and human-governed.

## Main-branch capabilities

The current `main` branch includes FastAPI, fail-closed API-key authentication, selected RBAC checks, tenant-scoped Engagement and Knowledge access, SQLAlchemy persistence, scope-aware planning, action-bound one-time approvals, a tamper-evident audit hash chain with HMAC checkpoint export, Findings, a typed tool catalogue with execution disabled, and bounded APK ZIP inspection.

The APK inspection endpoint is `POST /engagements/{engagement_id}/apk/inspect` with multipart field `file`. It computes SHA-256, validates archive limits, inventories DEX/native/resource/asset entries, and parses only plain-text XML manifests. It does not extract or execute the APK, persist the uploaded artifact, decompile DEX, decode binary Android XML, or verify APK signatures.

## Not yet executable

No integrated LLM runtime, MCP client, scanner/browser execution, active HTTP adapter, ADB device adapter, emulator manager, live Frida runtime, APK patch generator, APK re-signer, DEX decompiler, cryptographic signer verifier, or automated bypass/resilience harness is enabled in `main`. Android Skills and design documents are guidance, not live execution features.

## Quick start

Requires Python 3.12+:

```bash
git clone https://github.com/SockBoi-Hook-Patch/SockBoi-Agent.git
cd SockBoi-Agent
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Configure `SOCKBOI_API_KEYS` with server-side SHA-256 digests and start:

```bash
uvicorn sockboi.main:app --reload
```

Open http://127.0.0.1:8000/docs. Only `GET /health` is exempt from authentication. See the Thai setup section above for key generation and Docker instructions.

## Security

- Use only assets covered by explicit written authorization.
- Define Engagement scope and test windows before assessment.
- Keep API keys and checkpoint secrets outside source control.
- Use separate operator and reviewer principals.
- Require action-bound human approval for active/state-changing work.
- Treat APKs, Skills, model output, logs, and external content as untrusted.
- Do not add arbitrary shell execution, credential theft, stealth, persistence, destructive testing, denial-of-service, payment/licensing circumvention, or out-of-scope actions.
- Do not treat this Developer Preview as a production security control or proof that a target is secure.

See [SECURITY.md](SECURITY.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

## AI-assisted development

Parts of the documentation and development workflow were prepared with assistance from ChatGPT (OpenAI) and OpenAI Codex. These tools are acknowledged as AI assistance, not as repository owners or GitHub contributors.
