
from PySide6.QtCore import Signal, QObject
from pdf_utils import merge_and_optimize

class PDFMergeWorker(QObject):
    progress = Signal(dict)
    finished = Signal()

    def __init__(self, file_paths, output_file, jpeg_quality, compression):
        super().__init__()
        self.file_paths = file_paths
        self.output_file = output_file
        self.jpeg_quality = jpeg_quality
        self.compression = compression

    def run(self):
        merge_and_optimize(
            self.file_paths,
            self.output_file,
            jpeg_quality=self.jpeg_quality,
            compression_level=self.compression,
            progress_callback=self.progress.emit
        )
        self.finished.emit()