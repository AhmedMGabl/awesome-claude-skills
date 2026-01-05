import os
import zipfile
from pathlib import Path

# Skills to zip (excluding non-skill directories)
skills = [
    'artifacts-builder',
    'brand-guidelines',
    'canvas-design',
    'changelog-generator',
    'competitive-ads-extractor',
    'content-research-writer',
    'developer-growth-analysis',
    'domain-name-brainstormer',
    'file-organizer',
    'image-enhancer',
    'internal-comms',
    'invoice-organizer',
    'lead-research-assistant',
    'mcp-builder',
    'meeting-insights-analyzer',
    'raffle-winner-picker',
    'skill-creator',
    'slack-gif-creator',
    'template-skill',
    'theme-factory',
    'video-downloader',
    'webapp-testing'
]

# Create output directory
output_dir = Path('skill-zips')
output_dir.mkdir(exist_ok=True)

def zip_skill(skill_name):
    """Create a zip file for a skill directory"""
    skill_path = Path(skill_name)
    if not skill_path.exists():
        print(f"Skipping {skill_name} - directory not found")
        return

    zip_path = output_dir / f"{skill_name}.zip"

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_path):
            for file in files:
                file_path = Path(root) / file
                # Make paths relative to the skill directory itself, not its parent
                arcname = file_path.relative_to(skill_path)
                zipf.write(file_path, arcname)

    print(f"Created: {zip_path}")

# Zip all skills
print("Creating skill zip files...")
for skill in skills:
    zip_skill(skill)

print(f"\nDone! Created {len(skills)} zip files in the 'skill-zips' directory")
