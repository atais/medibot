const esbuild = require('esbuild');
const fs = require('fs');
const path = require('path');

const DIST_DIR = 'static/dist';
const DIST_HTML_FILE = 'templates/dist.html';
const SW_SRC = 'frontend/firebase-messaging-sw.js';
const APP_JS_SRC = 'frontend/app.entry.js';
const APP_CSS_SRC = 'frontend/app.entry.css';

// Clean dist directory before building
if (fs.existsSync(DIST_DIR)) {
  fs.rmSync(DIST_DIR, { recursive: true, force: true });
}

(async () => {
  // Step 1: Build service worker with hash in filename
  await esbuild.build({
    entryPoints: { sw: SW_SRC },
    outdir: DIST_DIR,
    bundle: true,
    minify: true,
    sourcemap: true,
    entryNames: 'firebase-messaging-sw-[hash]',
    format: 'iife',
    target: ['es2017'],
    loader: { '.js': 'js' },
    logLevel: 'info',
  });

  // Find the generated service worker filename
  const swFile = fs.readdirSync(DIST_DIR).find(f => /^firebase-messaging-sw-[a-zA-Z0-9]+\.js$/.test(f));
  if (!swFile) throw new Error('Service worker file not found');

  // Step 2: Build main JS, inject service worker filename
  await esbuild.build({
    entryPoints: { app: APP_JS_SRC },
    outdir: DIST_DIR,
    bundle: true,
    minify: true,
    sourcemap: true,
    entryNames: '[name].[hash]',
    format: 'iife',
    target: ['es2017'],
    loader: { '.js': 'js' },
    logLevel: 'info',
    define: {
      'SW_FILENAME': JSON.stringify(swFile)
    }
  });

  // Step 3: Build CSS
  await esbuild.build({
    entryPoints: { app: APP_CSS_SRC },
    outdir: DIST_DIR,
    bundle: true,
    minify: true,
    sourcemap: true,
    entryNames: '[name].[hash]',
    loader: { '.css': 'css', '.woff': 'file', '.woff2': 'file', '.ttf': 'file', '.eot': 'file', '.svg': 'file' },
    logLevel: 'info',
  });

  // Find the generated JS and CSS filenames
  const jsFile = fs.readdirSync(DIST_DIR).find(f => /^app\.[a-zA-Z0-9]+\.js$/.test(f));
  const cssFile = fs.readdirSync(DIST_DIR).find(f => /^app\.[a-zA-Z0-9]+\.css$/.test(f));
  if (!jsFile || !cssFile) throw new Error('JS or CSS file not found');

  // Step 4: Create dist.html with injected assets
  const distHtml = `<link rel="stylesheet" href="/static/dist/${cssFile}">\n` +
                    `<script src="/static/dist/${jsFile}"></script>\n`;
  fs.writeFileSync(DIST_HTML_FILE, distHtml);

  console.log(`Build complete: ${jsFile}, ${cssFile}, and ${swFile}.`);
})();
