"""Contributors: Aaron Antal-Bento (23013693)

Image helper functions."""

from PIL import Image, ImageDraw


def round_image_corners(image, radius):
    """Add rounded corners to an image."""
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), image.size], radius=radius, fill=255)

    output = Image.new("RGBA", image.size)
    output.paste(image, (0, 0))
    output.putalpha(mask)
    return output
