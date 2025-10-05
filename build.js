const esbuild = require('esbuild');
const fs = require('fs');
const crypto = require('crypto');
const path = require('path');

const TEMP_OUTFILE = 'static/dist/app.temp.js';
const TEMP_MAPFILE = 'static/dist/app.temp.js.map';
const DIST_DIR = 'static/dist';
const HTML_FILE = 'templates/head.html';

// Step 1: Build to temporary file with sourcemap
esbuild.build({
  entryPoints: ['frontend/app.entry.js'],
  bundle: true,
  minify: true,
  sourcemap: true,
  outfile: TEMP_OUTFILE,
  target: ['es2017'],
  format: 'iife',
  loader: { '.js': 'js' },
  logLevel: 'info',
}).then(() => {
  // Step 2: Calculate SHA256 hash of output
  const fileBuffer = fs.readFileSync(TEMP_OUTFILE);
  const hash = crypto.createHash('sha256').update(fileBuffer).digest('hex').slice(0, 8);
  const versionedName = `app.${hash}.js`;
  const versionedPath = path.join(DIST_DIR, versionedName);
  const versionedMapName = `app.${hash}.js.map`;
  const versionedMapPath = path.join(DIST_DIR, versionedMapName);

  // Step 3: Rename temp file and map file to versioned files
  fs.renameSync(TEMP_OUTFILE, versionedPath);
  fs.renameSync(TEMP_MAPFILE, versionedMapPath);

  // Step 4: Update sourceMappingURL in JS file to match new map name
  let jsContent = fs.readFileSync(versionedPath, 'utf8');
  jsContent = jsContent.replace(/(\n|\r)?\/\/\s*#\s*sourceMappingURL=app\.temp\.js\.map/, `\n//# sourceMappingURL=${versionedMapName}`);
  fs.writeFileSync(versionedPath, jsContent);

  // Step 5: Update head.html to reference new versioned file
  let html = fs.readFileSync(HTML_FILE, 'utf8');
  html = html.replace(/<script src="\/static\/dist\/app(\.[a-zA-Z0-9]+)?\.js"><\/script>/,
    `<script src="/static/dist/${versionedName}"></script>`);
  fs.writeFileSync(HTML_FILE, html);

  console.log(`Build complete: ${versionedName} and sourcemap injected.`);
}).catch((err) => {
  console.error('Build failed:', err);
  process.exit(1);
});
