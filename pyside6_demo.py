import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout
)


def main():
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Greeting Demo")

    layout = QVBoxLayout()

    # Welcome label
    welcome_label = QLabel("Welcome")
    welcome_label.setStyleSheet("font-size: 22px; font-weight: bold;")

    # Text box with prefill
    text_box = QLineEdit()
    text_box.setText("World")
    text_box.setStyleSheet("font-size: 18px;")

    # Submit button
    submit_button = QPushButton("Submit")

    # Output label (initially empty)
    output_label = QLabel("")
    output_label.setStyleSheet("font-size: 20px; color: #333;")

    def on_submit():
        name = text_box.text().strip()
        output_label.setText(f"Hello, {name}")

    submit_button.clicked.connect(on_submit)

    layout.addWidget(welcome_label)
    layout.addWidget(text_box)
    layout.addWidget(submit_button)
    layout.addWidget(output_label)

    window.setLayout(layout)
    window.resize(350, 200)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
