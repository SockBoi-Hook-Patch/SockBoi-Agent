# Architecture / สถาปัตยกรรม

## Design
SockBoi AI เป็น Control Plane สำหรับประเมินความปลอดภัยที่ได้รับอนุญาต ไม่ใช่ Unrestricted Exploit Runner

```text
Dashboard / API
      |
Engagement & Authorization
      |
Deterministic Policy Gate ---- Audit Log
      |
Multi-Agent Planner ---- Untrusted Knowledge Library
      |
Typed Tool Registry (catalog only; execution disabled)
      |
Approval Checkpoint (engagement + target + technique)
      |
Evidence SHA-256 utility (digest only; no persistence)
```

## Non-negotiable boundaries
1. Engagement ต้องมี Authorization Reference และ Asset Scope ที่ระบุชัด
2. Scope Check ทำงานแบบ deterministic และไม่ขึ้นกับผลลัพธ์ LLM
3. Tool Registry ใช้ Typed Schema; รุ่นนี้ยังไม่เปิด execution
4. Active Action ต้องมี Approval ที่ยังไม่หมดอายุและผูกกับ Engagement, Target, Technique
5. ผู้ร้องขออนุมัติไม่สามารถอนุมัติคำขอของตัวเอง
6. Skill, Markdown, Web Content และ Model Output เป็น Untrusted Data ไม่สามารถสั่ง Orchestrator หรือแก้ Policy
7. ไม่มี Arbitrary Shell, Reverse Shell, Persistence, Credential Theft หรือ DoS

## Current implementation
- FastAPI API, explicit scope models, deterministic planner
- Markdown ingestion สูงสุด 256 KB และ lexical retrieval ใน memory
- Static typed tool catalogue (ไม่ execute)
- Approval binding และ SHA-256 digest endpoint
- In-memory engagement, approval, finding, audit และ knowledge data

## Limitations
ยังไม่มี Authentication, RBAC, Tenant Isolation, PostgreSQL persistence, MCP Runtime, Browser/ZAP execution หรือ LLM Provider การตั้งค่า Docker database ยังไม่เชื่อมกับ application store ห้ามใช้ Production

## Roadmap
- PostgreSQL + migrations + transactional persistence
- Authenticated users, RBAC, tenant isolation
- MCP adapters แบบ allowlist พร้อม policy enforcement
- Browser/ZAP sandbox, egress allowlist, rate limits
- LLM planner ที่เสนอแผนเท่านั้น โดย Policy Engine เป็นผู้ตัดสิน
- Evidence storage, report generation และ evaluation suite
