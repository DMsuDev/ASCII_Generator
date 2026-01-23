from tkinter import Tk, filedialog
from pathlib import Path

def get_source_via_dialog(is_video: bool = False) -> str:
    """
    Open a file dialog to select an image or video file.
    Returns the selected file path or empty string if cancelled.
    """
    root = Tk()
    root.withdraw()  # Hide the main window

    if is_video:
        title: str = "Select Video File"
        file_types: list[tuple[str, str]] = [
            ("Video Files", "*.mp4 *.avi *.mov *.mkv *.webm"),
            ("All Files", "*.*"),
        ]
    else:
        title: str = "Select Image File"
        file_types: list[tuple[str, str]] = [
            ("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif"),
            ("All Files", "*.*"),
        ]

    file_path = filedialog.askopenfilename(
        parent=root,
        title=title,
        filetypes=file_types,
        initialdir=str(Path.home()),  # Better default: user home
    )

    root.destroy()  # Clean up
    return file_path