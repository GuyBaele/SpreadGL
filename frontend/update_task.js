const fs = require('fs');
const content = fs.readFileSync('/Users/u0150975/.gemini/antigravity/brain/057a5590-b511-4f01-900e-76e166456ef6/task.md', 'utf8');

const newContent = content.replace(
  /- `\[/\]` Fix Freezing Map Style Menu/,
  '- `[x]` Fix Freezing Map Style Menu'
).replace(
  /- `\[/\]` Restore Positron Icon/,
  '- `[x]` Restore Positron Icon'
);

fs.writeFileSync('/Users/u0150975/.gemini/antigravity/brain/057a5590-b511-4f01-900e-76e166456ef6/task.md', newContent);
