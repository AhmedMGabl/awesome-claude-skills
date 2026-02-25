OUT = r"W:\WS\AhmedGabl\awesome-claude-skills\rust-development\SKILL.md"
with open(OUT, "w", encoding="utf-8", newline="
") as f:
    f.write(CONTENT)
print(f"Written {len(CONTENT)} chars")
