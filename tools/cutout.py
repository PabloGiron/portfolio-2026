"""
Cuts the room out of its white background.
1. Flood-fills near-white from the image border (enclosed whites like the desk stay).
2. Shaves two more pixels off the edge, where the white had bled into the room.
3. Repaints the new edge pixels with colour from just inside, so no pale fringe is left.
4. Softens the edge slightly.
"""
import sys
import bpy
import numpy as np

# Usage: Blender -b --python tools/cutout.py -- <src> <dst> [min lightness] [max chroma] [x,y ...]
# Each extra x,y (pixels from the top-left) also clears an enclosed pocket of background.
args = sys.argv[sys.argv.index("--") + 1 :]
src, dst = args[0], args[1]
min_lightness = float(args[2]) if len(args) > 2 else 0.84
max_chroma = float(args[3]) if len(args) > 3 else 0.10
pockets = [tuple(int(n) for n in a.split(",")) for a in args[4:]]
image = bpy.data.images.load(src)
w, h = image.size
px = np.array(image.pixels[:], dtype=np.float32).reshape(h, w, 4)
rgb = px[:, :, :3].copy()


def grow(mask, diagonal=True):
    out = mask.copy()
    out[1:, :] |= mask[:-1, :]; out[:-1, :] |= mask[1:, :]
    out[:, 1:] |= mask[:, :-1]; out[:, :-1] |= mask[:, 1:]
    if diagonal:
        out[1:, 1:] |= mask[:-1, :-1]; out[1:, :-1] |= mask[:-1, 1:]
        out[:-1, 1:] |= mask[1:, :-1]; out[:-1, :-1] |= mask[1:, 1:]
    return out


# 1. Background: light, nearly colourless pixels connected to the border.
lightness = rgb.min(axis=2)
colourless = (rgb.max(axis=2) - rgb.min(axis=2)) < max_chroma
background_like = (lightness > min_lightness) & colourless
removed = np.zeros_like(background_like)
removed[0, :] = background_like[0, :]; removed[-1, :] = background_like[-1, :]
removed[:, 0] = background_like[:, 0]; removed[:, -1] = background_like[:, -1]
for x, y in pockets:
    removed[h - 1 - y, x] = background_like[h - 1 - y, x]
while True:
    bigger = grow(removed, diagonal=False) & background_like
    if (bigger == removed).all():
        break
    removed = bigger

# 2. Shave the contaminated rim.
removed = grow(grow(removed))

# 3. Repaint a 3 px band inside the new edge from clean interior colour.
band = removed
for _ in range(3):
    band = grow(band)
unknown = band & ~removed
known = ~band
for _ in range(4):
    total = np.zeros_like(rgb); count = np.zeros((h, w), dtype=np.float32)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue
            src_y = slice(max(0, -dy), h - max(0, dy)); dst_y = slice(max(0, dy), h - max(0, -dy))
            src_x = slice(max(0, -dx), w - max(0, dx)); dst_x = slice(max(0, dx), w - max(0, -dx))
            k = known[src_y, src_x]
            total[dst_y, dst_x] += rgb[src_y, src_x] * k[:, :, None]
            count[dst_y, dst_x] += k
    fill = unknown & (count > 0)
    rgb[fill] = total[fill] / count[fill][:, None]
    known = known | fill
    unknown = unknown & ~fill

# 4. Soft edge: average the hard mask over 3x3, never bringing removed pixels back.
solid = (~removed).astype(np.float32)
padded = np.pad(solid, 1, mode="edge")
blurred = sum(padded[y : y + h, x : x + w] for y in range(3) for x in range(3)) / 9.0
alpha = blurred * solid

px[:, :, :3] = rgb
px[:, :, 3] = alpha
out = bpy.data.images.new("cutout", w, h, alpha=True)
out.alpha_mode = "STRAIGHT"
out.pixels = px.ravel().tolist()
out.filepath_raw = dst
out.file_format = "PNG"
out.save()
print(f"transparent: {removed.mean():.1%} of the image, saved {dst}")
