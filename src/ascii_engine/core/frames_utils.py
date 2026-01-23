def scale_height(
    target_width: int,
    original_width: int,
    original_height: int,
    scale_factor: float = 0.43,
) -> int:
    """
    Calculate proportional height for ASCII rendering.
    Uses common terminal aspect ratio correction (~0.43–0.55).
    """
    if original_width == 0:
        return 0
    aspect_ratio = original_height / original_width
    return int(target_width * aspect_ratio * scale_factor)
