from pathlib import Path


def get_source_via_dialog(is_video: bool = False) -> str | None:
    """
    Open a file dialog to select an image or video file.
    Returns the selected file path or empty string if cancelled.
    """
    try:
        from tkinter import Tk, filedialog
    except ImportError as e:
        raise ImportError(
            "Not able to import tkinter for file dialog. "
            "In Docker/headless use --input directly instead of graphical dialog."
        ) from e

    root = Tk()
    root.withdraw()  # Hide the main window

    try:
        if is_video:
            file_types: list[tuple[str, str]] = [("Video Files", "*.mp4 *.avi *.mov *.mkv *.webm"), ("All Files", "*.*"),]
        else:
            file_types: list[tuple[str, str]] = [("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All Files", "*.*"),]

        path = filedialog.askopenfilename(
            parent=root,
            title="Select file" + (" of video" if is_video else ""),
            filetypes=file_types,
            initialdir=str(Path.home()),  # Better default: user home
        )
        return path if path else None
    except Exception as exc:
        print(f"Error occurred while opening file dialog: {exc}")
        return None
    finally:
        root.destroy()
