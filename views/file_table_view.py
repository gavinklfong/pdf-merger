from PyQt6.QtWidgets import QTableView, QWidget, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt


class FileTableView(QTableView):
    # ... existing code ...

    def create_action_widget(self, row, actions):
        """
        Create the action widget for a given row.
        `actions` is the UIActions controller instance.
        """
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 0, 5, 0)

        # Up
        up_btn = QPushButton("Up")
        up_btn.clicked.connect(actions.on_up_clicked)
        layout.addWidget(up_btn)

        # Down
        down_btn = QPushButton("Down")
        down_btn.clicked.connect(actions.on_down_clicked)
        layout.addWidget(down_btn)

        # View
        view_btn = QPushButton("View")
        view_btn.clicked.connect(actions.on_view_clicked)
        layout.addWidget(view_btn)

        # Remove
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(actions.on_remove_clicked)
        layout.addWidget(remove_btn)

        widget = QWidget()
        widget.setLayout(layout)

        index = self.model().index(row, 2)
        self.setIndexWidget(index, widget)
