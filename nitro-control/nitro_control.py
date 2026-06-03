#!/usr/bin/env python3
"""
Nitro Control — Acer ANV15-52 System Control Center
Main application entry point
"""

import sys
import os
import signal
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QMenu
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QUrl, Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QIcon, QAction

from backend import NitroBackend

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger('nitro-control')

APP_DIR = Path(__file__).parent
UI_PATH = APP_DIR / 'ui' / 'index.html'


class NitroWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Nitro Control — ANV15-52')
        self.setMinimumSize(1100, 720)
        self.resize(1100, 760)
        self.setWindowFlags(Qt.WindowType.Window)

        # Backend
        self.backend = NitroBackend(self)

        # WebView
        self.view = QWebEngineView()
        self.channel = QWebChannel()
        self.channel.registerObject('backend', self.backend)
        self.view.page().setWebChannel(self.channel)

        self.setCentralWidget(self.view)
        self.view.load(QUrl.fromLocalFile(str(UI_PATH)))
        self.view.loadFinished.connect(self._on_load)

        # Telemetry timer — polls hwmon every 3s
        self.telemetry_timer = QTimer()
        self.telemetry_timer.timeout.connect(self._push_telemetry)
        self.telemetry_timer.start(3000)

        # System tray
        self._setup_tray()

        log.info('Nitro Control window initialized')

    def _on_load(self, ok):
        if ok:
            log.info('UI loaded successfully')
            # Push initial state to JS
            self._push_telemetry()
            self._push_settings()
        else:
            log.error('UI failed to load')

    def _push_telemetry(self):
        """Read hwmon and push live data to JS"""
        data = self.backend.get_telemetry()
        js = f"window.updateTelemetry && window.updateTelemetry({data})"
        self.view.page().runJavaScript(js)

    def _push_settings(self):
        """Push current settings state to JS on startup"""
        settings = self.backend.get_all_settings()
        js = f"window.loadSettings && window.loadSettings({settings})"
        self.view.page().runJavaScript(js)

    def _setup_tray(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setToolTip('Nitro Control')

        tray_menu = QMenu()
        show_action = QAction('Show', self)
        show_action.triggered.connect(self.show)
        quit_action = QAction('Quit', self)
        quit_action.triggered.connect(QApplication.quit)

        tray_menu.addAction(show_action)
        tray_menu.addSeparator()

        # Quick profile actions
        for profile in ['low-power', 'quiet', 'balanced', 'balanced-performance', 'performance']:
            a = QAction(profile.replace('-', ' ').title(), self)
            a.triggered.connect(lambda checked, p=profile: self.backend.set_profile(p))
            tray_menu.addAction(a)

        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        self.tray.setContextMenu(tray_menu)
        self.tray.activated.connect(self._tray_activated)
        self.tray.show()

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show() if self.isHidden() else self.hide()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray.showMessage(
            'Nitro Control',
            'Running in system tray. Right-click the icon to quit.',
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    app.setApplicationName('Nitro Control')
    app.setOrganizationName('NitroControl')
    app.setQuitOnLastWindowClosed(False)

    window = NitroWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
