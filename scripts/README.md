Alembic runner and App Control workaround
=========================================

Why this exists
----------------
On some Windows setups Application Control policies (AppLocker / Defender Application Control)
prevent spawning console-script entry points installed by Python packages, which causes
commands like `alembic` to fail with an "Application Control policy has blocked this file" error.

What to use
-----------
This repository includes `scripts/alembic_runner.py` which invokes Alembic via its Python API,
avoiding the need to spawn the `alembic` executable. Use it like this:

```bash
python scripts/alembic_runner.py upgrade -c packages/storage/alembic.ini head
```

You can also run other Alembic actions:

```bash
python scripts/alembic_runner.py revision -c packages/storage/alembic.ini --autogenerate -m "add foo"
python scripts/alembic_runner.py downgrade -c packages/storage/alembic.ini -1
```

Permanent fix
-------------
- Work with your Windows administrator to whitelist the Python scripts directory or the `alembic` entry-point.
- Sign and allow the `alembic` entry-point executable if required by your policy.
- Alternatively, run migrations from a development container or CI runner that doesn't enforce the blocking policy.

Notes
-----
- This runner uses the Alembic Python API and requires the same Python environment that contains Alembic and your project dependencies.
- It is intended as a safe, buildable workaround — not a replacement for a formal policy change in production.
