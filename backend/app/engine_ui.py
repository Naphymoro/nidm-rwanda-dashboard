"""Shared offline interface for Studio, Workbench and Academy."""
from pathlib import Path

ASSETS = Path(__file__).with_name('engine_assets')


def engine_html(page):
    titles = {'studio': 'Research Studio', 'workbench': 'Research Workbench', 'academy': 'Learning Academy'}
    # The Studio is the chat interface; Workbench and Academy keep the form-based layout.
    template = 'chat.html' if page == 'studio' else 'index.html'
    return (ASSETS / template).read_text(encoding='utf-8').replace('__PAGE__', page).replace('__TITLE__', titles[page])
