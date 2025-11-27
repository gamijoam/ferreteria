from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QFrame,
    QSizePolicy,
    QDialog,
)
from PyQt6.QtCore import Qt


def _build_scroll_container(widget: QWidget, margins=(32, 32, 32, 32)) -> QVBoxLayout:
    root_layout = QVBoxLayout()
    root_layout.setContentsMargins(0, 0, 0, 0)
    root_layout.setSpacing(0)
    widget.setLayout(root_layout)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    root_layout.addWidget(scroll)

    container = QWidget()
    scroll.setWidget(container)

    container_layout = QVBoxLayout()
    container_layout.setContentsMargins(*margins)
    container_layout.setSpacing(20)
    container.setLayout(container_layout)
    return container_layout


def create_hero_card(title: str, subtitle: str = "", icon: str = "") -> QFrame:
    frame = QFrame()
    frame.setObjectName("heroCard")
    layout = QVBoxLayout()
    layout.setSpacing(8)
    frame.setLayout(layout)

    title_label = QLabel(f"{icon} {title}".strip())
    title_label.setProperty("class", "hero-title")
    title_label.setWordWrap(True)
    layout.addWidget(title_label)

    if subtitle:
        subtitle_label = QLabel(subtitle)
        subtitle_label.setProperty("class", "hero-subtitle")
        subtitle_label.setWordWrap(True)
        layout.addWidget(subtitle_label)

    return frame


def create_surface_card(title: str | None = None, subtitle: str | None = None) -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName("surfaceCard")
    frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

    layout = QVBoxLayout()
    layout.setContentsMargins(24, 20, 24, 24)
    layout.setSpacing(16)
    frame.setLayout(layout)

    if title:
        title_label = QLabel(title)
        title_label.setProperty("class", "section-title")
        layout.addWidget(title_label)
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setProperty("class", "section-subtitle")
            subtitle_label.setWordWrap(True)
            layout.addWidget(subtitle_label)

    return frame, layout


def create_badge(text: str, icon: str = "") -> QLabel:
    badge = QLabel(f"{icon} {text}".strip())
    badge.setProperty("class", "info-pill")
    badge.setAlignment(Qt.AlignmentFlag.AlignLeft)
    return badge


class ModernModuleWindow(QWidget):
    """Base window that provides a scrollable container and hero header."""

    def __init__(self, window_title: str, hero_title: str, hero_subtitle: str = "", icon: str = ""):
        super().__init__()
        self.setWindowTitle(window_title)
        self.setMinimumSize(1024, 640)
        self.resize(1180, 760)

        self._content_layout = _build_scroll_container(self)
        hero = create_hero_card(hero_title, hero_subtitle, icon)
        self._content_layout.addWidget(hero)

    def add_section(self, title: str | None = None, subtitle: str | None = None) -> QVBoxLayout:
        card, layout = create_surface_card(title, subtitle)
        self._content_layout.addWidget(card)
        return layout

    def add_custom_widget(self, widget: QWidget):
        self._content_layout.addWidget(widget)


class ModernDialog(QDialog):
    """Base dialog with consistent padding and hero header."""

    def __init__(self, title: str, hero_title: str | None = None, hero_subtitle: str = "", icon: str = "", parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(480)

        self._content_layout = _build_scroll_container(self, margins=(24, 24, 24, 24))
        if hero_title:
            hero = create_hero_card(hero_title, hero_subtitle, icon)
            self._content_layout.addWidget(hero)

    def add_section(self, title: str | None = None, subtitle: str | None = None) -> QVBoxLayout:
        card, layout = create_surface_card(title, subtitle)
        self._content_layout.addWidget(card)
        return layout

