# Hueb CLI

A small macOS-focused CLI for checking system status and cleaning common temporary folders.

## Requirements

- macOS
- Python 3.10+

## Install the CLI

Choose one of the options below.

### Option 1: Install as a global command (recommended)

From the project folder:

```bash
chmod +x hueb.py
sudo ln -sf "$(pwd)/hueb.py" /usr/local/bin/hueb
```

Now run:

```bash
hueb mac status
```

### Option 2: Run directly with Python

```bash
python3 hueb.py mac status
```

## Verify installation

```bash
hueb mac --help
```

If you used Option 2 (no global install), use:

```bash
python3 hueb.py mac --help
```

## Common commands

```bash
hueb mac status
hueb mac scan
hueb mac clean --dry-run
hueb mac clean --targets user_cache,user_logs
hueb mac find-clean --path . --names db,venv --dry-run
```
