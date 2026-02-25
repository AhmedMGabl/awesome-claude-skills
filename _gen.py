
import pathlib

BT = chr(96)*3

def b(lang=''):
    return BT + lang

def e():
    return BT

T = chr(0x251c)+chr(0x2500)+chr(0x2500)
L = chr(0x2514)+chr(0x2500)+chr(0x2500)
V = chr(0x2502)

t = pathlib.Path(r'W:/WS/AhmedGabl/awesome-claude-skills/react-native-mobile/SKILL.md')
t.parent.mkdir(parents=True, exist_ok=True)

# Read the content template
ct = pathlib.Path(r'W:/WS/AhmedGabl/awesome-claude-skills/_content_parts')
parts = []
for i in range(20):
    fp = ct / f'part_{i:02d}.txt'
    if fp.exists():
        parts.append(fp.read_text(encoding='utf-8'))

t.write_text(''.join(parts), encoding='utf-8')
print(f'Written {t.stat().st_size} bytes')
