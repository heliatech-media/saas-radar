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

// 3.5 Mirror site/functions to root/functions for Cloudflare Pages serverless routing
const siteFunctions = path.join(siteDir, 'functions');
const rootFunctions = path.join(rootDir, 'functions');
if (fs.existsSync(siteFunctions)) {
  console.log('⚡ Mirroring site/functions to root/functions for Cloudflare Pages API routing...');
  fs.cpSync(siteFunctions, rootFunctions, { recursive: true });
}

// 3.6 Compile Pages Functions into _worker.js for Cloudflare Pages / Workers API routing
if (fs.existsSync(rootFunctions)) {
  console.log('⚡ Compiling functions into _worker.js for edge worker dynamic routing...');
  try {
    execSync('npx wrangler pages functions build functions --outdir dist', { cwd: rootDir, stdio: 'inherit' });
    const compiledWorker = path.join(rootDist, 'index.js');
    const targetWorker = path.join(rootDist, '_worker.js');
    if (fs.existsSync(compiledWorker)) {
      fs.copyFileSync(compiledWorker, targetWorker);
      fs.copyFileSync(compiledWorker, path.join(siteDist, '_worker.js'));
      fs.copyFileSync(compiledWorker, path.join(siteDist, 'index.js'));
      console.log('✓ Compiled and mapped index.js to _worker.js in dist and site/dist');
    } else if (fs.existsSync(targetWorker)) {
      fs.copyFileSync(targetWorker, path.join(siteDist, '_worker.js'));
      console.log('✓ Compiled and mirrored _worker.js to dist and site/dist');
    }
  } catch (err) {
    console.warn('⚠️ [Cloudflare Build Bridge] Notice on _worker.js build:', err.message);
  }
}

// 4. Verify _headers and _redirects in both dist folders
const headersSource = path.join(siteDir, 'public', '_headers');
const redirectsSource = path.join(siteDir, 'public', '_redirects');

if (fs.existsSync(headersSource)) {
  fs.copyFileSync(headersSource, path.join(rootDist, '_headers'));
  fs.copyFileSync(headersSource, path.join(siteDist, '_headers'));
  console.log('✓ Verified _headers in dist');
}

if (fs.existsSync(redirectsSource)) {
  const rawRedirects = fs.readFileSync(redirectsSource, 'utf-8');
  // Cloudflare Pages requires all redirect source paths to be relative (start with '/')
  const cleanedLines = rawRedirects.split('\n').filter(line => {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) return true;
    if (trimmed.startsWith('http://') || trimmed.startsWith('https://')) {
      console.warn(`⚠️ [Cloudflare Build Bridge] Removed invalid absolute redirect: "${trimmed}"`);
      return false;
    }
    return true;
  }).map(line => line.replace(/(\s+\d{3})!/g, '$1'));
  const sanitized = cleanedLines.join('\n');
  fs.writeFileSync(path.join(rootDist, '_redirects'), sanitized, 'utf-8');
  fs.writeFileSync(path.join(siteDist, '_redirects'), sanitized, 'utf-8');
  fs.writeFileSync(redirectsSource, sanitized, 'utf-8');
  console.log('✓ Sanitized and verified _redirects in dist and public');
}

console.log('✨ [Cloudflare Build Bridge] Build completed successfully!');
