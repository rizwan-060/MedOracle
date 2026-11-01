import { readFileSync, readdirSync } from 'fs';
import { join } from 'path';

const srcDir = join(process.cwd(), 'src');
const errors = [];

function scanDir(dir) {
  const entries = readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = join(dir, entry.name);
    if (entry.isDirectory()) {
      scanDir(fullPath);
    } else if (entry.name.endsWith('.tsx') || entry.name.endsWith('.ts') || entry.name.endsWith('.jsx') || entry.name.endsWith('.js')) {
      if (entry.name === 'tokens.ts') continue;
      const content = readFileSync(fullPath, 'utf8');
      const hexColors = content.match(/#[0-9A-Fa-f]{3,8}\b/g);
      if (hexColors) {
        for (const c of hexColors) {
          errors.push(fullPath + ': contains raw hex color ' + c);
        }
      }
    }
  }
}

scanDir(srcDir);
if (errors.length > 0) {
  console.error('Lint errors:');
  errors.forEach(e => console.error(e));
  process.exit(1);
} else {
  console.log('Lint passed');
}
