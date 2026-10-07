# Frigate — 4 cameras, AI detection on the Pixel NPU

Frigate NVR in a Linux container, with object detection offloaded to the Pixel's Tensor NPU
over the network (DeepStack-compatible API). The Pi CM4 stays on **Kali** and just runs Docker.

```
Pi 3 + Cam v2 ──RTSP──┐
IP cam 2 ─────RTSP────┤        CM4 (Kali + Docker)                 Pixel 8 (Tensor NPU)
IP cam 3 ─────RTSP────┼──►  go2rtc → Frigate ──JPEG detect frames──►  /v1/vision/detection
IP cam 4 ─────RTSP────┘        Mosquitto ◄──► Home Assistant
```

| Path | What it is |
|------|------------|
| `docker-compose.yml` | Frigate + Mosquitto |
| `config/config.yml` | Frigate config: Pixel detector, go2rtc restream, 4 cameras |
| `.env.example` | Camera URLs and detector URL (copy to `.env`, which is git-ignored) |
| `mosquitto/config/` | LAN-only MQTT broker |
| `pi3-cam/` | MediaMTX config + systemd unit for the Pi 3 / Camera Module v2 |
| `stub-detector/` | Fake DeepStack server so you can test before the Pixel endpoint is live |

## 1. Pi 3 camera (Camera Module v2)

On Raspberry Pi OS Lite (Bookworm), check the camera works with `rpicam-hello --list-cameras`, then:

```bash
# grab the arm64 (64-bit OS) or armv7 (32-bit OS) build from
# https://github.com/bluenviron/mediamtx/releases
tar xzf mediamtx_*_linux_arm64.tar.gz mediamtx
sudo install mediamtx /usr/local/bin/
sudo install -m644 mediamtx.yml /usr/local/etc/mediamtx.yml
sudo install -m644 mediamtx.service /etc/systemd/system/
sudo systemctl enable --now mediamtx
```

Test from another machine: `ffplay rtsp://pi3.local:8554/cam`.

## 2. CM4 on Kali: Docker + Frigate

```bash
sudo apt install docker.io docker-compose
sudo apt-mark hold docker.io          # Kali is rolling — don't let apt upgrade break the NVR
sudo usermod -aG docker $USER

cd homelab/frigate
cp .env.example .env && $EDITOR .env  # camera URLs + Pixel detector URL
docker compose up -d
docker logs -f frigate                # first-run admin password is printed here
```

UI: `https://<cm4>:8971`. Put `FRIGATE_MEDIA_DIR` on a USB/NVMe SSD — continuous recording
wears out eMMC and SD cards fast.

Check the Pi decoder devices exist on Kali's kernel: `ls /dev/video1*` should show
`video10`–`video12`. If not, remove them from `docker-compose.yml` and delete the
`hwaccel_args` line in `config.yml` (CPU decode; workable for 4× 640×360 substreams).

## 3. Detection endpoint (Pixel)

Frigate POSTs each detect frame as a multipart JPEG (`image` field) and expects:

```json
{"success": true,
 "predictions": [{"label": "person", "confidence": 0.91,
                  "x_min": 120, "y_min": 40, "x_max": 260, "y_max": 330}]}
```

Labels must be COCO names (`person`, `car`, `dog`, …). Coordinates are pixels in the image
Frigate sent. The Pixel app must serve exactly this at `/v1/vision/detection`.

Until it does, run the stub on any machine and point `FRIGATE_DETECTOR_URL` at it:

```bash
python3 stub-detector/stub_detector.py --port 8080               # no detections
python3 stub-detector/stub_detector.py --port 8080 --fake-person # always a person, tests alerts
```

**Budget:** 4 cameras × 5 fps = up to 20 requests/s when there's motion (Frigate only sends
regions with motion). Keep the phone on USB-C Ethernet and the app's model loaded permanently.

## Running on the Acer instead

Same files. In `config.yml` set `hwaccel_args: preset-nvidia` (or `preset-vaapi` for the
iGPU), and in `docker-compose.yml` remove the `/dev/video*` devices (add the NVIDIA runtime
for `preset-nvidia`).

## Notes

- Config syntax targets Frigate 0.14–0.16 (`stable` tag). If a future release changes the
  `record.retain` layout, Frigate's log says which key it rejects.
- MQTT is anonymous on the LAN. Add a `password_file` before exposing it anywhere else.
