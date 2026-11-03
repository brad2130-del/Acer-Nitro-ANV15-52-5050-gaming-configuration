# Dungeon Sprites

Pixel-art sprites made from a hand-drawn picture (Skull Knight, Horned Door, Skull Key),
plus matching dungeon tiles.

| Sprite | Size | Frames |
|---|---|---|
| Skull Knight | 32x48 | 2 (idle bob) |
| Horned Door | 32x48 | closed / open |
| Skull Key | 16x32 | normal / sparkle |
| Torch | 16x16 | 2 (flicker) |
| Floor / Wall tiles | 16x16 | variants |

- `sprites/` – native-size PNGs with transparency (best for game engines; scale with nearest-neighbour)
- `sprites_4x/` – same, 4x larger
- `strip_*.png` – animation frames side by side
- `sprite_sheet_preview.png`, `dungeon_scene.png`, `dungeon_scene.gif` – previews

Regenerate with `python3 generate_sprites.py` (needs Pillow).
