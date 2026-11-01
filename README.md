# SockBoi Agent

**Policy-first AI security assessment planning for explicitly authorized environments.**

[![CI](https://github.com/SockBoi-Hook-Patch/SockBoi-Agent/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/SockBoi-Hook-Patch/SockBoi-Agent/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-0.3.1-orange)](https://github.com/SockBoi-Hook-Patch/SockBoi-Agent)

> **สถานะ / Status: v0.3.1 — Developer Preview**
>
> SockBoi Agent is an early-stage foundation for planning and governing authorized security assessments. It is **not a production-ready penetration-testing platform or an autonomous scanner**. Several integrations and security controls are not implemented yet.

- [ภาษาไทย](#ภาษาไทย)
- [English](#english)
- [Architecture](#architecture)
- [Security status and limitations](#security-status-and-limitations)
- [Development](#development)
- [Contributing](#contributing)

---

## ภาษาไทย

### SockBoi Agent คืออะไร

SockBoi Agent เป็นโครงการต้นแบบสำหรับช่วยวางแผนและจัดการกระบวนการประเมินความปลอดภัยไซเบอร์ในระบบที่ได้รับอนุญาตอย่างชัดเจน โดยออกแบบให้ Agent ช่วยเสนอแผนและจัดระเบียบข้อมูล ขณะที่การตรวจสอบ Scope และ Policy แยกเป็นส่วนควบคุมของระบบ

หลักการออกแบบ:
- **Scope first:** ทุก Engagement ต้องกำหนดเป้าหมายและขอบเขตที่ได้รับอนุญาต
- **Policy over prompts:** ผลลัพธ์จาก AI และเนื้อหาใน Skills/Knowledge เป็นข้อมูลที่ไม่น่าเชื่อถือ ไม่สามารถเปลี่ยน Policy ได้
- **Human oversight:** การทดสอบเชิงรุกต้องมีการตรวจสอบและอนุมัติโดยมนุษย์ก่อน
- **Least capability:** เครื่องมือที่ยังไม่พร้อมใช้งานจริงจะไม่เปิดให้ execute
- **Auditability:** ออกแบบให้ติดตามเหตุการณ์และการตัดสินใจได้

### ความสามารถที่มีใน v0.3.1

- **Multi-agent planning:** แบ่งบทบาทการวางแผนระหว่าง Guard, Hunter, API, Network และ Analyst
- **Scope validation:** ตรวจสอบ Domain, URL, IP และ CIDR เทียบกับ Scope ของ Engagement
- **Knowledge ingestion:** นำเข้า Markdown และค้นหาด้วย Keyword โดยถือว่าเอกสารเป็น Untrusted Reference Data
- **Typed tool registry:** แสดงรายการเครื่องมือและ Input Schema โดยยังไม่เปิดการ Execute
- **Approval workflow foundation:** มีโมเดลคำขออนุมัติและการตรวจสอบเงื่อนไขบางส่วน แต่ยังไม่มีการยืนยันตัวตน/สิทธิ์ผู้อนุมัติที่เชื่อถือได้
- **Evidence digest:** คำนวณ SHA-256 จากข้อมูลที่ส่งเข้ามา โดยไม่จัดเก็บเนื้อหาหลักฐาน
- **Audit events:** บันทึกเหตุการณ์ของ Engagement, Plan, Approval และ Policy ใน Store ปัจจุบัน

### เริ่มต้นใช้งาน

ต้องใช้ Python 3.12 ขึ้นไป

```bash
git clone https://github.com/SockBoi-Hook-Patch/SockBoi-Agent.git
cd SockBoi-Agent

python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\\Scripts\\Activate.ps1

python -m pip install -e ".[dev]"
uvicorn sockboi.main:app --reload
```

เปิดเอกสาร API ที่ http://127.0.0.1:8000/docs

> ใช้เฉพาะเครื่องทดสอบในเครื่องตัวเอง อย่าเปิด API นี้สู่เครือข่ายที่ไม่น่าเชื่อถือ

### Workflow ที่ตั้งใจรองรับ

1. สร้าง Engagement และระบุเอกสารอ้างอิงการอนุญาตกับ Asset ที่อยู่ใน Scope
2. ให้ Planner สร้างแผนจาก Target ภายใน Scope
3. ตรวจสอบแผน ความเสี่ยง และขั้นตอนด้วยตนเอง
4. ใช้ Approval workflow เป็นโครงสร้างประกอบการควบคุมก่อน Active Check
5. ตรวจสอบ Audit Events และข้อมูล Finding

Workflow นี้เป็นภาพรวมของความสามารถต้นแบบ ไม่ได้หมายความว่าระบบสามารถรันการทดสอบหรือบังคับใช้การอนุมัติอย่างปลอดภัยครบวงจรแล้ว

### API หลัก

| Endpoint | หน้าที่ |
|---|---|
| `GET /health` | ตรวจสอบสถานะและเวอร์ชัน |
| `POST /engagements` | สร้าง Engagement |
| `POST /engagements/{id}/plan` | สร้างแผนการประเมิน |
| `POST /engagements/{id}/approvals` | สร้างคำขออนุมัติ |
| `POST /approvals/{id}/decide` | บันทึกผลการตัดสินใจคำขอ |
| `POST /policy/check` | ตรวจสอบ Policy |
| `POST /knowledge/ingest` | นำเข้า Markdown |
| `GET /knowledge/search` | ค้นหา Knowledge |
| `GET /tools` | ดู Typed Tool Registry |
| `POST /evidence/hash` | คำนวณ SHA-256 Digest |

ดูรายละเอียด Request/Response ที่ API Docs หลังเริ่มเซิร์ฟเวอร์

---

## English

### Overview

SockBoi Agent is an early-stage, policy-oriented foundation for planning authorized security assessments. It separates agent-generated planning from deterministic scope and policy checks, and is organized around three concepts: **Agent**, **Skills**, and **MCP**.

It currently provides planning and control-plane foundations—not a live pentest execution engine.

### Implemented in v0.3.1

- Multi-role assessment planning.
- Domain, URL, IP, and CIDR scope validation.
- Markdown knowledge ingestion and keyword retrieval. Imported content is treated as untrusted reference data.
- Typed tool catalogue with execution disabled.
- Approval workflow models and partial validation checks. Approver identity and authorization are not securely established yet.
- SHA-256 evidence digest endpoint; submitted evidence content is not persisted by that endpoint.
- In-memory audit events.

### Quick start

Requires Python 3.12+.

```bash
git clone https://github.com/SockBoi-Hook-Patch/SockBoi-Agent.git
cd SockBoi-Agent
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
uvicorn sockboi.main:app --reload
```

On Windows PowerShell, activate the environment with `.venv\\Scripts\\Activate.ps1`.

Open http://127.0.0.1:8000/docs.

### Intended workflow

1. Define an engagement and its explicitly authorized assets.
2. Generate a plan for in-scope targets.
3. Review the proposed steps and risks.
4. Use the approval workflow as a prototype control before any active assessment.
5. Review audit events and findings.

The current implementation does not execute scanners, browsers, or external assessment tools.

---

## Architecture

The project is organized into three modular areas:

- **Agent Core** — planning and orchestration.
- **Skills** — versioned assessment playbooks and reference knowledge.
- **MCP** — typed integration foundations for tools and services.

The Policy Engine is intended to remain the authority for scope and action decisions. Agent output, Skills, and ingested Knowledge must always be treated as untrusted input.

See:
- [Agent documentation](agent/README.md)
- [Skills documentation](skills/README.md)
- [MCP documentation](mcp/README.md)
- [Architecture](docs/architecture.md)
- [Agent system](docs/agent-system.md)
- [Roadmap](docs/roadmap.md)

## Security status and limitations

**Do not deploy this version in production or expose it to untrusted networks.**

Known limitations in v0.3.1:

- No API authentication or authenticated user identity.
- No user-level RBAC or tenant isolation.
- Approval decisions accept caller-supplied approver identity; the current self-approval check is not a trustworthy authorization boundary.
- Data is stored in process memory and is lost when the process exits.
- Audit records are not durable or tamper-evident.
- The typed tool registry is a catalogue; there is no live MCP transport or tool execution.
- No scanner, browser, or ZAP execution layer is connected to the API.
- No LLM runtime is integrated into the application flow.

The project intentionally does not provide unrestricted shell execution, credential theft, persistence, denial-of-service functionality, or out-of-scope assessment behavior.

Only use the project in a local development environment with systems you own or are explicitly authorized to assess. Review [SECURITY.md](SECURITY.md) before testing.

## Development

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
```

## Contributing

Contributions are welcome, especially improvements to correctness, tests, documentation, and security boundaries. Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## License

The repository currently declares MIT in package metadata. Review the repository's license file and distribution terms before reuse.

## AI-assisted development

This project is developed and maintained by its human project owner. AI tools are used as development aids:

- **ChatGPT (OpenAI):** used for technical discussion, planning, code/documentation review, and drafting assistance.
- **OpenAI Codex:** used for coding assistance, repository changes, and development workflows.

AI-generated suggestions are reviewed and validated by the project maintainer. These tools are acknowledged as development assistance, not as GitHub contributors, project owners, or substitutes for human responsibility.
