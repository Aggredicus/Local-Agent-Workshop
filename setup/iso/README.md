# Offline Debian + LAW installer

Builds a custom **Debian 13.7.0 amd64 netinst** ISO, using the user's requested official image. The Linux/GitHub build downloads and authenticates that ISO, downloads the complete signed Debian and official Docker package closure, installs it in a disconnected test container, and remasters both BIOS/UEFI boot entries. No Python, Git, WSL or Docker Desktop is required on Windows to download/use the finished image.

This installs the LAW CLI, editable source workspace, encrypted USB Wi-Fi controller, official Docker Engine, Compose v2 and Buildx. Docker runs rootless for the normal account created in the installer; rootful Docker/containerd services are masked. No containers are pulled at installation time. `/opt/law-offline/smoke.tar` is a tiny authenticated BusyBox test workload: `docker load -i /opt/law-offline/smoke.tar; docker run --rm --network none law-offline-smoke:1`.

The broader multi-service orchestration/dashboard remains separate unfinished work. This image does not deploy the paused legacy experiment.

## Build automatically

Open **Actions → Build LAW offline Debian ISO → Run workflow** in GitHub. The workflow downloads the base, builds, verifies and tests the result. On main, successful builds publish a test-candidate release with one ISO, SHA256, source/package evidence and VM results. Download the ISO to Desktop with menu option 2 in the Windows tools. The Windows downloader checks the checksum before completing the file.

To customize a build, edit `setup/iso/profile.json` on a branch and run the workflow there. Inputs are deliberately limited to nonsecret hostname, locale, keyboard, timezone and an optional Ed25519 **public** SSH key. No passwords, private keys, Wi-Fi credentials or shell commands are accepted. Default timezone is America/New_York; change it before building if needed.

To build locally on amd64 Linux with Docker, Python 3.11+, xorriso, dpkg-deb, gpgv and the distro-authenticated `debian-keyring` package:

```sh
PYTHONPATH=src python3 -m workshop.iso.build --output /tmp/law-iso-build
# Equivalent installed CLI: workshop iso build --output /tmp/law-iso-build
```

Use a new output directory. Builds preserve incomplete output for diagnosis and never overwrite an existing build. Allow at least 12 GB free and internet on the builder. The target needs no internet. If the exact upstream image moves or signature metadata expires, the build/install fails rather than weakening signature verification; rebuild with reviewed updated inputs. The profile currently accepts only the specified Debian 13.7.0 amd64 version.

## Install (erases the disk you approve)

Use a 32 GB or larger USB. Initialize it with official Ventoy after confirming its target device; Ventoy initialization erases that USB. Copy the verified LAW ISO to its DATA volume, alongside the LAW tools folder. Windows tools are ordinary files; booting the USB starts the Debian installer. The builder/downloader never formats a disk.

Boot ThinkCentre2 from USB and select **LAW offline Debian + rootless Docker**. **Choose the destination disk and confirm partition writes in Debian Installer.** Production preseed deliberately contains no disk, partition scheme, erase confirmation, username or password. Create one normal account locally. Net access is disabled during the install; the signed file repositories supply LAW dependencies. Debian's included firmware is available to its normal hardware detection.

Keep the installer USB inserted until installation completes. After reboot, run `docker info`, `docker compose version`, `docker buildx version`, and `workshop --help`. Read `/etc/motd` for Wi-Fi pairing and SSH. Wi-Fi credentials must be entered/tested on Windows **after** Debian generates its local pairing key; only the public request and encrypted capsule travel on USB. SSH stays disabled unless a public key was included or you run `sudo law-enable-ssh /path/to/public-key.pub` locally.

Qualification is reported per build. A disconnected container proves package closure; disposable BIOS/UEFI VM checks do not qualify a physical USB, Secure Boot or the ThinkCentre Wi-Fi chipset. Never publish the QA-only unattended ISO or virtual disk: they contain synthetic test account answers. The public ISO always retains disk confirmation.
