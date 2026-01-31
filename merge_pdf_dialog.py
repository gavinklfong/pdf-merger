from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QPushButton
)
from PySide6.QtCore import Qt

COMPRESSION_LABELS = ["Low", "Medium", "High", "Highest"]

class MergePDFDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Compression Settings")

        layout = QVBoxLayout(self)

        # --- Compression Level Slider ---
        layout.addWidget(QLabel("Compression Level:"))

        self.compSlider = QSlider(Qt.Horizontal)
        self.compSlider.setTickPosition(QSlider.TicksBelow)
        self.compSlider.setTickInterval(1)
        self.compSlider.setRange(0, 3)
        self.compSlider.setValue(1)
        layout.addWidget(self.compSlider)

        self.compLabel = QLabel("Medium")
        self.compLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.compLabel)

        self.compSlider.valueChanged.connect(self.updateCompressionLabel)

        # --- JPEG Quality Slider ---
        layout.addWidget(QLabel("JPEG Quality (1–100):"))

        self.jpegSlider = QSlider(Qt.Horizontal)
        self.jpegSlider.setTickPosition(QSlider.TicksBelow)
        self.jpegSlider.setTickInterval(10)
        self.jpegSlider.setRange(1, 100)
        self.jpegSlider.setValue(80)
        layout.addWidget(self.jpegSlider)

        # Live JPEG quality label
        self.jpegLabel = QLabel("80")
        self.jpegLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.jpegLabel)

        self.jpegSlider.valueChanged.connect(self.updateJPEGLabel)

        # --- OK / Cancel Buttons ---
        buttonRow = QHBoxLayout()

        self.okBtn = QPushButton("OK")
        self.cancelBtn = QPushButton("Cancel")

        self.okBtn.clicked.connect(self.accept)
        self.cancelBtn.clicked.connect(self.reject)

        buttonRow.addWidget(self.okBtn)
        buttonRow.addWidget(self.cancelBtn)

        layout.addLayout(buttonRow)


    # Map slider → text
    def updateCompressionLabel(self, value):
        self.compLabel.setText(COMPRESSION_LABELS[value])

    # Update JPEG quality label
    def updateJPEGLabel(self, value):
        self.jpegLabel.setText(str(value))

    # Return values to caller
    def getValues(self):
        return {
            "compression": COMPRESSION_LABELS[self.compSlider.value()],
            "jpeg_quality": self.jpegSlider.value()
        }
