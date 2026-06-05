# AGENTS.md

## Cursor Cloud specific instructions

### Product overview

Atom is a hackable desktop text editor (Electron 2.0.12). Development is a single-app workflow driven by `script/bootstrap`, `script/build`, `script/lint`, and `script/test` — see the [Flight Manual build docs](https://flight-manual.atom.io/hacking-atom/sections/hacking-on-atom-core/#platform-linux).

### Required toolchain

| Component | Version / notes |
|-----------|-----------------|
| Node.js | **8.9.3** via nvm (`nvm install 8.9.3`) |
| npm | **6.2.0** (`npm install -g npm@6.2.0 --ignore-scripts`) — required for `npm ci` |
| Python | **2.7.18** via pyenv — required by node-gyp for native modules |
| Compiler | **gcc-10 / g++-10** — gcc 13 breaks `superstring` native builds |
| Display | **Xvfb on `:99`** for GUI/tests (`Xvfb :99 -ac -screen 0 1280x1024x24 &`) |

### Dead atom.io registry workaround

The atom.io package API and Electron download host were sunset. Before `script/bootstrap`, run:

```bash
python3 scripts/patch-atom-registry.py
```

This rewrites bundled-package URLs in `package.json` / `package-lock.json` to GitHub tarballs and drops stale integrity hashes. Also set:

```bash
export ATOM_ELECTRON_URL=https://artifacts.electronjs.org/headers/dist
```

### Runtime libraries

The built Electron binary needs legacy **libgconf-2** (not in Ubuntu 24.04 repos). Extract from an older Ubuntu package into `$HOME/atom-libs/gconf` and add to `LD_LIBRARY_PATH`:

```bash
export LD_LIBRARY_PATH=$HOME/atom-libs/gconf/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
```

Also install: `libdbus-glib-1-2`, `libgtk2.0-0`, `libnotify4`, `libxtst6`, `libnss3`.

### Standard commands

See `script/` for the canonical entry points:

| Task | Command |
|------|---------|
| Install deps | `script/bootstrap --ci` |
| Build | `script/build` (use `--existing-binaries` to resume after a partial build) |
| Lint | `script/lint` |
| Test | `script/test` (Linux runs **main-process specs only**; many GUI specs timeout under Xvfb) |
| Run built app | `./out/atom-dev-1.34.0-dev-amd64/atom [path]` |

### Environment variables (add to shell before build/test/run)

```bash
export NVM_DIR="$HOME/.nvm" && . "$NVM_DIR/nvm.sh" && nvm use 8.9.3
export PYENV_ROOT="$HOME/.pyenv" && eval "$(pyenv init -)"
export PATH="$PYENV_ROOT/versions/2.7.18/bin:$PATH"
export PYTHON="$PYENV_ROOT/versions/2.7.18/bin/python"
export DISPLAY=:99
export CC=gcc-10 CXX=g++-10
export ATOM_ELECTRON_URL=https://artifacts.electronjs.org/headers/dist
export LD_LIBRARY_PATH=$HOME/atom-libs/gconf/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
```

### Gotchas

- Only one built binary should exist under `out/` — remove stale `atom-dev-*` dirs before `script/test`.
- `script/build` invokes `script/bootstrap` first; bootstrap is slow (~5+ min) due to native module compilation.
- Headless GUI tests frequently time out; lint + successful build + launching the binary are reliable verification signals.
