import { readFileSync, readdirSync } from 'fs';
import { join } from 'path';

const designsDir = join(process.cwd(), 'designs-refs');
const files = readdirSync(designsDir).filter(f => f.endsWith('.dc.html'));

const tokenCounts = {
  colors: new Map(),
  fontFamilies: new Map(),
  fontSizes: new Map(),
  fontWeights: new Map(),
  borderRadii: new Map(),
  boxShadows: new Map(),
  spacing: new Map(),
};

function addToMap(map, value, file) {
  if (!map.has(value)) {
    map.set(value, { count: 0, files: new Set() });
  }
  const entry = map.get(value);
  entry.count++;
  entry.files.add(file);
}

for (const file of files) {
  const content = readFileSync(join(designsDir, file), 'utf8');
  
  const hexColors = content.match(/#[0-9A-Fa-f]{3,8}\b/g) || [];
  for (const c of hexColors) {
    addToMap(tokenCounts.colors, c.toLowerCase(), file);
  }
  
  const rgbColors = content.match(/rgb\([^)]+\)/g) || [];
  for (const c of rgbColors) {
    addToMap(tokenCounts.colors, c, file);
  }
  
  const fontFamilies = content.match(/font-family[^;]+/g) || [];
  for (const f of fontFamilies) {
    const match = f.match(/font-family:\s*([^;]+)/);
    if (match) {
      addToMap(tokenCounts.fontFamilies, match[1].trim(), file);
    }
  }
  
  const twFont = content.match(/font-(sans|serif|mono|Lexend|Newsreader)[^\s"')]*/g) || [];
  for (const f of twFont) {
    addToMap(tokenCounts.fontFamilies, f, file);
  }
  
  const fontSizes = content.match(/text-\[([^\]]+)\]/g) || [];
  for (const f of fontSizes) {
    addToMap(tokenCounts.fontSizes, f, file);
  }
  
  const fontWeights = content.match(/font-(thin|extralight|light|normal|medium|semibold|bold|extrabold|black|\[[^\]]+\])[^\s"')]*/g) || [];
  for (const f of fontWeights) {
    addToMap(tokenCounts.fontWeights, f, file);
  }
  
  const roundedBrackets = content.match(/rounded-\[([^\]]+)\]/g) || [];
  for (const r of roundedBrackets) {
    addToMap(tokenCounts.borderRadii, 'rounded-[' + r.match(/\[([^\]]+)\]/)[1] + ']', file);
  }
  
  const shadows = content.match(/shadow-\[([^\]]+)\]/g) || [];
  for (const s of shadows) {
    const m = s.match(/\[([^\]]+)\]/);
    if (m) addToMap(tokenCounts.boxShadows, 'shadow-[' + m[1] + ']', file);
  }
  
  const spacing = content.match(/(?:p|px|py|pt|pb|pl|pr|m|mx|my|mt|mb|ml|mr|gap)-\[([^\]]+)\]/g) || [];
  for (const s of spacing) {
    addToMap(tokenCounts.spacing, s, file);
  }
}

function printMap(name, map) {
  console.log('\n=== ' + name + ' ===');
  const sorted = Array.from(map.entries()).sort((a, b) => b[1].count - a[1].count);
  for (const [value, info] of sorted) {
    console.log(value.padEnd(70) + ' | count: ' + info.count + ' | files: ' + Array.from(info.files).join(', '));
  }
}

printMap('COLORS', tokenCounts.colors);
printMap('FONT FAMILIES', tokenCounts.fontFamilies);
printMap('FONT SIZES', tokenCounts.fontSizes);
printMap('FONT WEIGHTS', tokenCounts.fontWeights);
printMap('BORDER RADII', tokenCounts.borderRadii);
printMap('BOX SHADOWS', tokenCounts.boxShadows);
printMap('SPACING', tokenCounts.spacing);
