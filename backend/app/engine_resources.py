"""Measured resource envelope; never change a scientific method implicitly."""
import importlib.util
import importlib.metadata
import os
import platform
from pathlib import Path

from .encoding import PROVIDER_DEFAULTS


def resources():
    cpu = len(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else (os.cpu_count() or 1)
    memory = None
    try:
        fields = dict(line.split(':', 1) for line in Path('/proc/meminfo').read_text().splitlines())
        memory = int(fields['MemAvailable'].split()[0]) * 1024
    except (OSError, KeyError, ValueError):
        pass
    try:
        maximum = Path('/sys/fs/cgroup/memory.max').read_text().strip()
        used = int(Path('/sys/fs/cgroup/memory.current').read_text())
        if maximum != 'max':
            available = max(0, int(maximum) - used)
            memory = min(memory, available) if memory is not None else available
    except (OSError, ValueError):
        pass
    try:
        quota, period = Path('/sys/fs/cgroup/cpu.max').read_text().split()
        if quota != 'max':
            cpu = min(cpu, max(1, int(quota) // int(period)))
    except (OSError, ValueError):
        pass
    constrained = cpu < 2 or memory is None or memory < 2 * 1024**3
    return {
        'cpu_available': cpu, 'memory_available_mb': round(memory / 1024**2) if memory is not None else None,
        'recommended_profile': 'economy' if constrained else 'balanced',
        'worker_limit': 1 if constrained else 2,
        'connectivity': 'not_probed', 'network_required': False,
        'dependencies': {name: importlib.util.find_spec(name) is not None for name in ('numpy', 'scipy', 'torch', 'pyro')},
        'providers': [{'name': name, 'credentials_configured': bool(os.getenv(config['env']))}
                      for name, config in PROVIDER_DEFAULTS.items() if config.get('env')],
        'provider_note': 'Credential presence only; connectivity and model availability are not inferred. This harness uses local domain tools.',
        'profiles': {'economy': 3, 'balanced': 7, 'thorough': 11},
    }


def environment_manifest():
    packages = {}
    for name in ('fastapi', 'pydantic', 'numpy', 'scipy', 'torch', 'pyro-ppl'):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    return {'python': platform.python_version(), 'platform': platform.system(), 'packages': packages,
            'random_seed': None, 'seed_reason': 'Selected engine tools are deterministic; no random sampling.'}
