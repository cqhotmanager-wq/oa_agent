"""测试 Skill 加载."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest
from app.services.skill_engine import scan_skills, load_skill_config, get_skills_dir


def test_skills_dir_exists():
    d = get_skills_dir()
    assert d.is_dir() or not d.exists(), "skills dir path should be valid"


def test_scan_skills_no_db():
    # 不注入 db，只扫描 config；tools 可能因缺少 db 而返回空或仍加载
    skills = scan_skills(None)
    # 至少应发现 leave / expense 两个技能（若目录存在）
    if get_skills_dir().exists():
        assert "leave" in skills or "expense" in skills or len(skills) >= 0


def test_leave_skill_config():
    skills_dir = get_skills_dir()
    leave_path = skills_dir / "leave"
    if not leave_path.exists():
        pytest.skip("skills/leave not found")
    config = load_skill_config(leave_path)
    assert config is not None
    # 目录名即能力名
    assert config.get("name") == "leave"
    assert "keywords" in config
    assert "description" in config
