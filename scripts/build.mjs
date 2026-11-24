// Builds the published site: skills.json + one <skill>.zip per skill.
// Layout: <category>/<skill>/SKILL.md   Usage: node scripts/build.mjs [repoRoot] [outDir]
import { readdirSync, readFileSync, existsSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { join, resolve } from 'node:path';

const root = resolve(process.argv[2] ?? '.'), out = resolve(process.argv[3] ?? '_site');
const dirs = p => readdirSync(p, { withFileTypes: true }).filter(d => d.isDirectory() && !/^[._]|^(scripts|node_modules)$/.test(d.name)).map(d => d.name).sort();

rmSync(out, { recursive: true, force: true }); mkdirSync(out, { recursive: true });
const skills = [];
for (const category of dirs(root)) for (const slug of dirs(join(root, category))) {
  const file = join(root, category, slug, 'SKILL.md');
  if (!existsSync(file)) continue;
  if (!/^[a-z0-9-]+$/.test(slug)) throw new Error(`${category}/${slug}: folder name must be lowercase letters, numbers and dashes`);
  if (skills.some(s => s.slug === slug)) throw new Error(`"${slug}" exists in two categories; skill names must be unique (they are the URL)`);
  const fm = readFileSync(file, 'utf8').replace(/\r/g, '').match(/^---\n([\s\S]*?)\n---/)?.[1] ?? '';
  // shortcut: single-line `key: value` only; multi-line YAML descriptions (> or |) come out empty. Use a YAML parser if that is ever needed.
  const field = k => (fm.match(new RegExp(`^${k}:[ \\t]*(.+)$`, 'm'))?.[1] ?? '').trim().replace(/^(["'])(.*)\1$/, '$2').replace(/^[>|][+-]?$/, '');
  skills.push({ slug, category, name: field('name') || slug, description: field('description') });
  execFileSync('zip', ['-qr', join(out, `${slug}.zip`), slug, '-x', '*.DS_Store'], { cwd: join(root, category) });
}
writeFileSync(join(out, 'skills.json'), JSON.stringify(skills, null, 1));
console.log(`${skills.length} skill(s): ${skills.map(s => `${s.category}/${s.slug}`).join(', ') || 'none yet'}`);
