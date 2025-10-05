const esbuild = require('esbuild');
const fs = require('fs');
const crypto = require('crypto');
const path = require('path');

const DIST_DIR = 'static/dist';
const HTML_FILE = 'templates/head.html';
const TEMP_JS_OUTFILE = path.join(DIST_DIR, 'app.temp.js');
const TEMP_JS_MAPFILE = path.join(DIST_DIR, 'app.temp.js.map');
const TEMP_CSS_OUTFILE = path.join(DIST_DIR, 'app.temp.css');

// Step 1: Build JS
esbuild.build({
  entryPoints: ['frontend/app.entry.js'],
  bundle: true,
  minify: true,
  sourcemap: true,
  outfile: TEMP_JS_OUTFILE,
  target: ['es2017'],
  format: 'iife',
  loader: { '.js': 'js' },
  logLevel: 'info',
}).then(() => {
  // Step 2: Build CSS
  return esbuild.build({
    entryPoints: ['frontend/app.entry.css'],
    bundle: true,
    minify: true,
    outfile: TEMP_CSS_OUTFILE,
    loader: { '.css': 'css', '.woff': 'file', '.woff2': 'file', '.ttf': 'file', '.eot': 'file', '.svg': 'file' },
    logLevel: 'info',
  });
}).then(() => {
  // Step 3: Hash and rename JS
  const jsBuffer = fs.readFileSync(TEMP_JS_OUTFILE);
  const jsHash = crypto.createHash('sha256').update(jsBuffer).digest('hex').slice(0, 8);
  const jsVersionedName = `app.${jsHash}.js`;
  const jsVersionedPath = path.join(DIST_DIR, jsVersionedName);
  const jsMapVersionedName = `app.${jsHash}.js.map`;
  const jsMapVersionedPath = path.join(DIST_DIR, jsMapVersionedName);
  fs.renameSync(TEMP_JS_OUTFILE, jsVersionedPath);
  if (fs.existsSync(TEMP_JS_MAPFILE)) {
    fs.renameSync(TEMP_JS_MAPFILE, jsMapVersionedPath);
  }
  let jsContent = fs.readFileSync(jsVersionedPath, 'utf8');
  jsContent = jsContent.replace(/(\n|\r)?\/\/\s*#\s*sourceMappingURL=app\.temp\.js\.map/, `\n//# sourceMappingURL=${jsMapVersionedName}`);
  fs.writeFileSync(jsVersionedPath, jsContent);

  // Step 4: Hash and rename CSS
  const cssBuffer = fs.readFileSync(TEMP_CSS_OUTFILE);
  const cssHash = crypto.createHash('sha256').update(cssBuffer).digest('hex').slice(0, 8);
  const cssVersionedName = `app.${cssHash}.css`;
  const cssVersionedPath = path.join(DIST_DIR, cssVersionedName);
  fs.renameSync(TEMP_CSS_OUTFILE, cssVersionedPath);

  // Step 5: Inject CSS and JS under <!-- AUTO INJECT BELOW --> in head.html
  let html = fs.readFileSync(HTML_FILE, 'utf8');
  const injectTag = '<!-- AUTO INJECT BELOW -->';
  const injectContent = `\n<link rel="stylesheet" href="/static/dist/${cssVersionedName}">\n<script src="/static/dist/${jsVersionedName}"></script>\n`;
  const idx = html.indexOf(injectTag);
  if (idx !== -1) {
    const before = html.slice(0, idx + injectTag.length);
    html = before + injectContent;
    fs.writeFileSync(HTML_FILE, html);
    console.log(`Injected CSS and JS under ${injectTag} in head.html.`);
  } else {
    console.error(`Could not find ${injectTag} in head.html.`);
  }

  console.log(`Build complete: ${jsVersionedName} and ${cssVersionedName} injected into head.html.`);
}).catch((err) => {
  console.error('Build failed:', err);
  process.exit(1);
});
