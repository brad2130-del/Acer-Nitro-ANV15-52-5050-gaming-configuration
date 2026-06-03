# NOTICE — linuwu_sense

`linuwu_sense.c` in this directory is **derived from the upstream Linuwu-Sense project**, the
community kernel module that exposes Acer Nitro/Predator hardware controls through `acer-wmi`
sysfs. It is included here for reproducibility and because this machine's setup may carry local
patches.

- Upstream: https://github.com/0x7375646F/Linuwu-Sense
- License: **GPL** (per upstream). Any redistribution of this file must comply with the upstream
  license. See `../LICENSE` for how this interacts with the rest of the repo.

If you maintain this repo: prefer pointing users at upstream + shipping only a *diff* of any local
patches, rather than vendoring the full GPL source, unless you intend the whole repo to be GPL.

Module load notes for the ANV15-52 (see `../nitro-control/README.md` for the GUI side):
- Load with `nitro_v4=1` (else it falls back to hardcoded profiles and fan control misbehaves).
- Blacklist `acer_wmi` — it races `linuwu_sense` on boot and prevents it binding.
