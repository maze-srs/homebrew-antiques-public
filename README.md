# Homebrew Antiques

Source code for **Homebrew Antiques**, a short visual novel made in **2 hours** for a game jam.

**Play it in your browser:** https://fleetingglance.itch.io/homebrew-antiques

Built with [Ren'Py](https://www.renpy.org/) 8.6.

---

## About the code
The whole game lives in one file: `game/script.rpy`

### The inventory system explained
The inventory is the most heavily commented part of the project. Look for `screen inventory_screen` in `game/script.rpy`. It is written so that someone new to Ren'Py screens can follow it line by line.

What it does:
- Shows a grid of items. Hovering an item shows its **name and value** in an info box.
- Clicking an item closes the screen and **returns the item's name** to the story.
- An optional **Back** button returns `"back"` instead.

How it works:
- The items live in one list, `shop_items`. Each entry is `(name, value, icon colour)`, so adding an item is one new line.
- Each button carries its item as a `tooltip`, and `GetTooltip()` reads it back to fill the info box.
- `Return(...)` is the button's `action`, and the story reads the answer from `_return`.

Using it in the story:
```renpy
call screen inventory_screen(can_go_back=False)   # no Back button: the player must pick

if _return != "Plain White Mask":
    masked "Mh... this is not what I'm searching for..."
    jump masked_mask_search                       # ask again
```
---

## Art
The artwork is **not included** in this repository (the `game/images/` folder is intentionally empty). The game still runs: missing sprites and backgrounds are replaced by coloured placeholder figures.

## Credits
- Code: on Itch: https://maze-jk.itch.io/ on GitHub: https://github.com/maze-srs
- Writing: on Itch: https://fleetingglance.itch.io/ and https://itch.io/profile/literally-leon
- Art: on Itch: https://itch.io/profile/starlava20
- Music and sound effects (royalty free) from:  https://pixabay.com/ and https://freesound.org/

## License
The artwork belongs to its artist and is not covered by the code's license.