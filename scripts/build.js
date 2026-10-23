import { execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');
const siteDir = path.join(rootDir, 'site');
const siteDist = path.join(siteDir, 'dist');
const rootDist = path.join(rootDir, 'dist');

console.log('🚀 [Cloudflare Build Bridge] Starting multi-root compatible build...');
console.log(`📁 Root: ${rootDir}`);
console.log(`📁 Site: ${siteDir}`);

// 1. Install dependencies in site
console.log('📦 Ensuring site dependencies are installed...');
execSync('npm install', { cwd: siteDir, stdio: 'inherit' });

// 2. Run Astro build in site
console.log('⚡ Running Astro compilation...');
execSync('npm run build', { cwd: siteDir, stdio: 'inherit' });

// 3. Mirror site/dist to root/dist
console.log('📋 Mirroring site/dist to root/dist for Cloudflare Pages output compatibility...');
if (fs.existsSync(rootDist)) {
  fs.rmSync(rootDist, { recursive: true, force: true });
}
fs.cpSync(siteDist, rootDist, { recursive: true });

// 4. Verify _headers and _redirects in both dist folders
const headersSource = path.join(siteDir, 'public', '_headers');
const redirectsSource = path.join(siteDir, 'public', '_redirects');

if (fs.existsSync(headersSource)) {
  fs.copyFileSync(headersSource, path.join(rootDist, '_headers'));
  fs.copyFileSync(headersSource, path.join(siteDist, '_headers'));
  console.log('✓ Verified _headers in dist');
}

if (fs.existsSync(redirectsSource)) {
  fs.copyFileSync(redirectsSource, path.join(rootDist, '_redirects'));
  fs.copyFileSync(redirectsSource, path.join(siteDist, '_redirects'));
  console.log('✓ Verified _redirects in dist');
}

console.log('✨ [Cloudflare Build Bridge] Build completed successfully!');
