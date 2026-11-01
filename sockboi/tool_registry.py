"""Static typed tool catalogue. No arbitrary MCP server or tool invocation is exposed."""
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ToolSpec:
    tool_id: str
    description: str
    input_schema: dict
    risk: str
    execution_enabled: bool = False


TOOL_CATALOG: tuple[ToolSpec, ...] = (
    ToolSpec(
        "knowledge.search",
        "ค้นหาเอกสารความรู้ที่นำเข้าไว้แบบ lexical retrieval",
        {"type": "object", "required": ["query"],
         "properties": {"query": {"type": "string"}, "limit": {"type": "integer"}}},
        "passive",
    ),
    ToolSpec(
        "evidence.sha256",
        "คำนวณ SHA-256 ของหลักฐานที่ผู้ใช้ส่งมา โดยไม่จัดเก็บไฟล์",
        {"type": "object", "required": ["content"],
         "properties": {"content": {"type": "string"}}},
        "passive",
    ),
    ToolSpec(
        "scope.inspect",
        "ตรวจสอบว่าเป้าหมายอยู่ใน Engagement scope หรือไม่",
        {"type": "object", "required": ["engagement_id", "target"],
         "properties": {"engagement_id": {"type": "string"}, "target": {"type": "string"}}},
        "passive",
    ),
)


def list_tools() -> list[dict]:
    return [asdict(item) for item in TOOL_CATALOG]
