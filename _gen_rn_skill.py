#!/usr/bin/env python3
import pathlib

target = pathlib.Path(r"W:/WS/AhmedGabl/awesome-claude-skills/react-native-mobile/SKILL.md")
# Read the template from the companion .txt file
content = pathlib.Path(r"W:/WS/AhmedGabl/awesome-claude-skills/_rn_skill_content.txt").read_text(encoding="utf-8")
target.write_text(content, encoding="utf-8")
print(f"Written {target.stat().st_size} bytes to {target}")
