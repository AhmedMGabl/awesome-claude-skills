const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');
fs.writeFileSync('W:/WS/AhmedGabl/awesome-claude-skills/prisma-orm/SKILL.md', content, 'utf8');
console.log('Written:', content.length, 'chars');