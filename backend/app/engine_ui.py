"""Shared offline interface for Studio, Workbench and Academy."""
from pathlib import Path

ASSETS = Path(__file__).with_name('engine_assets')


def engine_html(page):
    titles = {'studio': 'Research Studio', 'workbench': 'Research Workbench', 'academy': 'Learning Academy'}
    return (ASSETS / 'index.html').read_text(encoding='utf-8').replace('__PAGE__', page).replace('__TITLE__', titles[page])
