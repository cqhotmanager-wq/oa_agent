"""Skill Engine - 动态加载 skills 目录下的技能（SKILL.md + tools.py）。目录名描述能力，SKILL.md 为技能描述。"""
import importlib.util
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml


def get_skills_dir() -> Path:
    """返回项目根目录下的 skills 目录路径（可从配置覆盖）。"""
    try:
        from config.settings import settings
        base = Path(settings.skills_dir)
    except Exception:
        base = Path(__file__).resolve().parents[2] / "skills"
    if not base.is_absolute():
        base = Path(__file__).resolve().parents[2] / base
    return base


def _parse_skill_md(content: str) -> Dict[str, Any]:
    """解析 SKILL.md：可选 YAML frontmatter（--- ... ---）+ 正文。"""
    data: Dict[str, Any] = {}
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", content, re.DOTALL)
    if match:
        fm, body = match.group(1).strip(), match.group(2).strip()
        if fm:
            try:
                data = yaml.safe_load(fm) or {}
            except yaml.YAMLError:
                pass
        data["_body"] = body
    else:
        data["_body"] = content.strip()
    return data


def load_skill_config(skill_path: Path) -> Optional[Dict[str, Any]]:
    """读取 skills/xxx/SKILL.md。技能名以目录名（能力名）为准。"""
    skill_file = skill_path / "SKILL.md"
    if not skill_file.exists():
        return None
    with open(skill_file, "r", encoding="utf-8") as f:
        raw = _parse_skill_md(f.read())
    # 目录名描述能力，作为 name/namespace
    name = skill_path.name
    config = {
        "name": name,
        "description": raw.get("description") or raw.get("_body", "")[:200],
        "namespace": raw.get("namespace", name),
        "keywords": raw.get("keywords", []),
    }
    if "_body" in raw:
        config["_body"] = raw["_body"]
    return config


def load_skill_tools(skill_path: Path, get_db_session: Optional[Callable] = None) -> List[Any]:
    """动态加载 skills/xxx/tools.py 中的 make_xxx_tools(get_db_session)，返回工具列表。"""
    tools_file = skill_path / "tools.py"
    if not tools_file.exists():
        return []
    spec = importlib.util.spec_from_file_location("skill_tools", tools_file)
    if spec is None or spec.loader is None:
        return []
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # 优先已知工厂名，否则查找任意 make_*_tools
    factory_name = None
    for name in ["make_leave_tools", "make_expense_tools", "make_tools"]:
        if hasattr(mod, name):
            factory_name = name
            break
    if factory_name is None:
        for attr in dir(mod):
            if attr.startswith("make_") and attr.endswith("_tools"):
                factory_name = attr
                break
    if factory_name is None:
        return []
    factory = getattr(mod, factory_name)
    if get_db_session is None:
        def _no_db():
            yield None
        get_db_session = _no_db
    return factory(get_db_session)


def scan_skills(get_db_session: Optional[Callable] = None) -> Dict[str, Dict[str, Any]]:
    """
    扫描 skills 目录下所有子目录，每个有 SKILL.md 的目录视为一个技能。
    返回 { skill_name: { "config": {...}, "tools": [...], "path": str } }。
    """
    skills_dir = get_skills_dir()
    if not skills_dir.exists():
        return {}
    result = {}
    for item in skills_dir.iterdir():
        if not item.is_dir():
            continue
        config = load_skill_config(item)
        if not config:
            continue
        name = config.get("name") or item.name
        tools = load_skill_tools(item, get_db_session)
        result[name] = {"config": config, "tools": tools, "path": str(item)}
    return result
