# LineageOS 21 — SIM "!" Symbol (Not Activated / No Service)

**Symptom:** After flashing LineageOS 21, the signal bar area shows an **exclamation mark (!)** next
to or replacing the normal signal quality bars. Calls, SMS, and/or mobile data don't work.

---

## What the "!" Actually Means

LineageOS (and AOSP) uses the exclamation mark for two distinct problems that look identical:

| Icon state | What it means |
|------------|---------------|
| `!` next to bars, bars show signal | Registered on carrier, but **mobile data cannot reach the internet** (data activated but no IP connectivity / captive portal) |
| `!` with no bars / X / empty | **Not registered on the network** — the SIM is not provisioned, the IMEI is broken, or the radio can't find a compatible band |
| Bars present but grayed + `!` | Registered for voice/SMS only, data APN is wrong or blocked |

Identify which case you're in before chasing the wrong fix.

---

## Step 1 — Check Your IMEI

The single most common cause of post-flash SIM failure is a **null or all-zeros IMEI**. Flashing a
custom recovery or ROM does not normally wipe the IMEI, but a bad flash, wrong firmware, or wiping
`/persist` partition can.

**Dial `*#06#`** on the phone app.

- If it shows a valid 15-digit IMEI → IMEI is fine, go to Step 2.
- If it shows `000000000000000`, `null`, or nothing → the IMEI is gone. This is the root cause.

### Restoring a lost IMEI

The IMEI is stored in the `/persist` or `/efs` partition (device-dependent). It is **not** in the
ROM you flashed — it comes from the device's factory partition.

1. If you have a TWRP backup that included `/persist` or `/efs`, restore just that partition.
2. If not, check if the IMEI is printed on the original box or under the battery cover — you will
   need it to restore via `nvram` or `qpst` tools (Qualcomm) or MTK equivalent.
3. Do **not** attempt to write a different device's IMEI — that is illegal in most jurisdictions.

---

## Step 2 — Toggle Airplane Mode

The simplest fix. After flashing, the radio stack sometimes needs a full cycle:

1. Pull down the notification shade → enable **Airplane Mode** → wait 10 seconds.
2. Disable Airplane Mode → wait 30–60 seconds for the carrier search to complete.
3. If the `!` disappears, you're done.

If the `!` persists, hard-reboot (`Power + Volume Down`) and try again.

---

## Step 3 — Re-seat the SIM Card

Power off completely. Remove the SIM, inspect for lint/corrosion, reinsert firmly. Power back on.
LineageOS occasionally fails to initialize the SIM slot properly on first boot after a flash.

---

## Step 4 — Set the Correct APN

A `!` alongside visible signal bars almost always means the APN (Access Point Name) is wrong or
missing. LineageOS imports carrier APN databases, but yours may not be populated.

**Settings → Network & Internet → SIMs → [your SIM] → Access Point Names**

If the list is empty or has only generic entries:

1. Tap the **+** to add a new APN.
2. Get the correct APN settings from your carrier's website (search `[carrier name] APN settings
   Android`). You need at minimum: **Name**, **APN**, **MCC**, **MNC**, **APN type** (`default,supl`
   for data; add `mms` if you want MMS).
3. Save, then select the new APN as active.
4. Toggle airplane mode to force a re-registration.

---

## Step 5 — Force the Preferred Network Type

If your carrier has deployed VoLTE-only (some carriers decommissioned 2G/3G), LineageOS defaulting
to an older network type will leave the SIM with `!`.

**Settings → Network & Internet → SIMs → [your SIM] → Preferred network type**

Try these in order, waiting ~30 seconds between each:

1. **LTE/WCDMA/GSM (auto)** — try this first
2. **LTE only** — forces 4G, useful if 3G is decommissioned
3. **NR/LTE/WCDMA/GSM** — if your carrier is 5G and the device supports it

If switching to LTE-only makes the `!` disappear, your carrier has shut down 3G/2G in your area.

---

## Step 6 — Manual Network Selection

Automatic carrier selection can get stuck on a carrier that's either the wrong one or one with no
signal in your area.

**Settings → Network & Internet → SIMs → [your SIM] → Carrier → Select automatically → OFF**

Wait for the scan to complete. A list of visible networks appears. Pick yours. If yours isn't listed
at all, the SIM/IMEI problem (Step 1) or a radio firmware mismatch (Step 8) is the likely cause.

---

## Step 7 — Check VoLTE / IMS State

Some carriers require VoLTE to be active, and some LineageOS builds ship with it disabled or
missing IMS support for certain devices.

**Settings → Network & Internet → SIMs → [your SIM] → VoLTE calls** — toggle it on if present.

If the VoLTE toggle doesn't exist, your LineageOS build may not include IMS blobs for your device.
Check the LineageOS wiki page for your specific device model to see if VoLTE is listed as
supported. If it isn't, a community-built IMS/VoLTE addon may be available (search `[device
codename] IMS LineageOS`).

---

## Step 8 — Verify Radio Firmware Matches Your LineageOS Build

LineageOS does **not** bundle modem/radio firmware — it comes from the stock firmware of your
device. If you flashed LineageOS without first updating the stock firmware to the expected version,
the radio may be incompatible.

1. Check the LineageOS wiki page for your device model: look for the **"Before installing"** or
   **"Firmware"** section. It will list the minimum stock firmware version required.
2. On the phone: **Settings → About phone → Android version / Build number** — note the LineageOS
   version and the baseband version shown under **Baseband version**.
3. If the baseband version is lower than what LineageOS requires, download the stock firmware zip
   for your device (from the manufacturer or XDA), boot to TWRP, and flash **only the firmware**
   (not the stock system). Then reboot to LineageOS.

---

## Step 9 — Call Your Carrier

If all of the above pass, the SIM may simply need **re-provisioning** on the carrier side. This is
common when:

- You put a SIM from an old phone into a newly flashed device and the carrier's network thinks the
  device changed unexpectedly.
- The carrier uses CDMA or eSIM-style provisioning that must be re-triggered.

Call carrier support and say: *"I changed phones and my SIM shows no service — can you
re-provision or re-activate my SIM?"* They can push an OTA provisioning update to the SIM remotely.
Sometimes they'll ask for your IMEI (have it ready from `*#06#`).

For **US CDMA carriers (Verizon, older Sprint)** specifically: dial `*228` → option 1 from a
working phone on the same line to trigger provisioning, or call support.

---

## Step 10 — Captive Portal Detection (Data Works But Shows "!")

If calls and SMS work but data shows `!` even though pages load in the browser, the issue is
LineageOS's captive portal check hitting a blocked endpoint.

LineageOS 21 (AOSP-based) pings `connectivitycheck.gstatic.com` to detect internet connectivity.
If that domain is blocked by your carrier, a corporate VPN, or a DNS filter, you'll get a permanent
`!` even with fully working data.

**Fix — point captive portal check at a different server:**

Using ADB (with USB debugging enabled):

```bash
adb shell settings put global captive_portal_http_url http://connectivitycheck.lineageos.org/
adb shell settings put global captive_portal_https_url https://connectivitycheck.lineageos.org/
adb shell settings put global captive_portal_use_https 1
```

Or disable the check entirely (not recommended — breaks some hotspot/VPN detection):

```bash
adb shell settings put global captive_portal_mode 0
```

Reboot after either change.

---

## Diagnostic Checklist

| Check | How | Expected |
|-------|-----|----------|
| IMEI present | Dial `*#06#` | 15-digit number, not zeros |
| Baseband visible | Settings → About phone → Baseband version | Non-empty string |
| SIM recognized | Settings → Network & Internet → SIMs | SIM listed with carrier name |
| Network registered | Settings → Network & Internet → SIMs → [SIM] | "Connected" or carrier name shown |
| APN configured | Settings → Network & Internet → SIMs → APN | At least one APN with correct values |
| VoLTE state | Settings → Network & Internet → SIMs → VoLTE | Matches carrier requirement |

---

## If Nothing Works

- Flash the **stock ROM** back, confirm the SIM works, then re-flash LineageOS. This isolates
  whether the problem is the ROM or the SIM/carrier.
- Check **XDA Developers** for your specific device codename — search `[codename] LineageOS 21
  SIM` to find known device-specific issues (missing blobs, wrong partition flash order, etc.).
- Check the **LineageOS issue tracker** on GitLab for open bugs against your device.
