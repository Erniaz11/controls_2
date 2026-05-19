import sys

from PyQt6.QtWidgets import QApplication

import database
from ui import create_main_window


def main():
    database.init_db()
    app = QApplication(sys.argv)
    window = create_main_window()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()