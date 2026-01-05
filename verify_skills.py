import zipfile
from pathlib import Path
import sys

def verify_skill_zip(zip_path):
    """Verify a skill zip file has correct structure and is not corrupted"""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Test integrity
            if zf.testzip() is not None:
                return False, "Corrupted"

            # Check for SKILL.md at root
            files = zf.namelist()
            if 'SKILL.md' not in files:
                return False, "No SKILL.md at root"

            # Read and verify SKILL.md has YAML frontmatter
            skill_content = zf.read('SKILL.md').decode('utf-8')
            if not skill_content.startswith('---'):
                return False, "Missing YAML frontmatter"

            # Check if it has name and description
            lines = skill_content.split('\n')
            has_name = any('name:' in line for line in lines[:10])
            has_desc = any('description:' in line for line in lines[:10])

            if not has_name or not has_desc:
                return False, "Missing name or description"

            return True, f"OK ({len(files)} files)"

    except Exception as e:
        return False, str(e)

# Test all zips
skill_zips = Path('skill-zips')
if not skill_zips.exists():
    print("skill-zips directory not found!")
    sys.exit(1)

print("Verifying all skill zip files...\n")
print(f"{'Skill Name':<35} {'Status':<10} {'Details'}")
print("-" * 70)

all_good = True
for zip_file in sorted(skill_zips.glob('*.zip')):
    name = zip_file.stem
    is_valid, message = verify_skill_zip(zip_file)

    status = "[OK]" if is_valid else "[ERROR]"
    print(f"{name:<35} {status:<10} {message}")

    if not is_valid:
        all_good = False

print("\n" + "=" * 70)
if all_good:
    print("[SUCCESS] All skills are valid and ready to upload!")
else:
    print("[WARNING] Some skills have issues - check above for details")
