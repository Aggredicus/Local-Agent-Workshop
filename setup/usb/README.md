# One USB: Windows setup, Debian installation, safe Wi-Fi recovery

Use a **32 GB or larger** USB with Ventoy's exFAT/NTFS data partition. ThinkCentre1 keeps its existing Windows 11 installation. ThinkCentre2 keeps its existing Debian installation for the recovery workflow.

This tools ZIP **is not bootable by itself and contains no Debian installer ISO**. It supplies Windows tools plus real offline recovery packages. Booting requires a separately verified official Debian ISO and Ventoy. No program here formats a disk or reinstalls Debian automatically.

## 1. Prepare on Windows — no WSL, Git or Python required

1. Download the prepared LAW USB tools ZIP and its SHA256. **Compare the hash with the value supplied independently alongside the download**, before executing anything:

   ```powershell
   Get-FileHash -Algorithm SHA256 -LiteralPath .\LAW-USB-Tools.zip
   Expand-Archive -LiteralPath .\LAW-USB-Tools.zip -DestinationPath .\LAW-USB-Tools
   ```

   A checksum file on the same untrusted USB is not an independent trust anchor. Keep the verified extracted folder on Windows; returning USB files must never replace this trusted code.
2. Open `LAW-USB-Tools\LAW` and run `START-USB.cmd`. Choose **1** to stage the credential-entry tools into `%LOCALAPPDATA%\LocalAgentWorkshop\USBTools`. The new per-user folder has restricted ACLs. The age executable is additionally checked against a pinned SHA256 before any credentials are requested.
3. If PowerShell blocks a downloaded script, stop and inspect it. No launcher changes execution policy or bypasses it. After checking the ZIP and reviewing the script, you can explicitly unblock the extracted scripts with `Unblock-File` from PowerShell. If no organisation policy applies and you explicitly choose to allow the reviewed scripts for the current PowerShell window only, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`, then launch the script from that window. Do not override organisation policy or use `Bypass`. Native Windows PowerShell 5.1 is the supported target, but native testing remains outstanding in this cloud environment.

## 2. Make the same USB boot Debian

1. Obtain Ventoy only through its [official download page](https://www.ventoy.net/en/download.html) and follow its integrity-verification instructions. Run its Windows utility yourself. Select the USB by its capacity/device identity and approve initialization. **Initial installation erases that selected USB.** Back up its existing contents first. This is separate from copying LAW files.
2. Obtain the current supported Debian **amd64 DVD-1 ISO** from the [official Debian DVD directory](https://cdimage.debian.org/debian-cd/current/amd64/iso-dvd/). DVD-1 is preferable to netinst when the target has no internet. Follow [Debian's verification instructions](https://www.debian.org/CD/verify), including authenticated signing-key fingerprints, signature verification of SHA512SUMS, and matching the ISO's SHA512. Gpg4win/GnuPG is an optional Windows prerequisite for OpenPGP verification; do not treat a hash match alone as an upstream signature check.
3. Copy the verified ISO onto Ventoy's DATA volume. Use exFAT/NTFS because DVD-1 may exceed FAT32's file-size limit.
4. From the original verified LAW folder on Windows, choose **3** in START-USB. Select the Ventoy DATA drive (for example `E:\`). Only manifest-listed, hash-checked files are copied to a new `LAW` folder; existing data/LAW folders are not overwritten. No private key or plaintext credentials belong on this USB.
5. Test the USB boot menu on the physical machine. Use its firmware boot menu; do not change internal-disk partitioning. Secure Boot behavior depends on the Ventoy version and firmware; follow the official procedure and review any key-enrollment request. These scripts do not disable Secure Boot or enroll keys.

**Recovery is not installation.** ThinkCentre2 already boots, so boot installed Debian normally to fix its network. Selecting a Debian installer and changing disk partitions is a separate deliberate operator action. Read-only rescue/inspection does not authorize reinstallation.

## 3. Install recovery tools offline on Debian

At the physical Debian console, log in normally. Insert/mount the USB data partition using your existing mount workflow. Find its mount path with `lsblk -f`; do not guess a `/dev/sdX` device, format it, or mount an internal disk as a substitute. Example below assumes `/media/usb/LAW`; replace that with the actual mount point.

```sh
bash /media/usb/LAW/setup/usb/inspect.sh
cat /etc/debian_version
```

Choose the bundle matching the **installed** Debian major version and amd64 architecture:

```sh
# Debian 12:
bash /media/usb/LAW/setup/usb/packages.sh verify /media/usb/LAW/packages/debian12-amd64
sudo bash /media/usb/LAW/setup/usb/packages.sh install /media/usb/LAW/packages/debian12-amd64
# On Debian 13, use debian13-amd64 instead.
```

The verifier uses Debian's already-installed archive trust root and `gpgv` or Debian 13's `sqv`. It checks signed InRelease metadata, freshness, package-index hashes, package hashes, target release/architecture and the complete dependency closure. A correct clock and an authenticated Debian keyring/verifier are prerequisites. It stages bounded data privately, shows an actual APT plan, requires `INSTALL`, removes no existing packages and downloads nothing. It targets only fixed recovery tools; it does not install Docker, NetworkManager or an SSH server. Package maintainer scripts still run as root after approval.

No matching bundle, missing archive trust/verifier, expired metadata, broken dpkg transaction, wrong architecture or missing firmware is reported as success. Use authenticated Debian installation media or temporary Ethernet if those prerequisites cannot be met. No APT trust or signature bypass is used.

## 4. Pair Debian; only its public key goes to Windows

Install trusted controller code locally **before** the USB makes a round trip:

```sh
sudo bash /media/usb/LAW/setup/usb/install-controller.sh
sudo law-usb pair --output /media/usb/debian-request.json
```

Confirm the trusted ZIP hash before controller installation. The private age key remains in root-only `/var/lib/local-agent-workshop/usb-wifi/identity.age-key`. The request JSON contains only a public recipient, a fingerprint, a one-day nonce/expiry and hostname. Record the displayed fingerprint to compare independently on Windows. Never copy the private key to USB, Windows, chat, a report or a repository.

The controller requires a root physical virtual console (`/dev/tty1`, `/dev/tty2`, etc.). In a desktop terminal, switch with Ctrl+Alt+F3 and log in. SSH/pseudo-terminal network changes are intentionally unsupported in this first recovery path.

## 5. Enter and optionally test credentials on Windows

Return the USB to Windows. **Use the trusted locally staged script**, not executables or scripts on the returning USB:

```powershell
& "$env:LOCALAPPDATA\LocalAgentWorkshop\USBTools\setup\usb\Wifi-Capsule.ps1"
```

Select the public `debian-request.json`, enter the fingerprint displayed by Debian, and choose an encrypted-output directory on the USB. Enter the SSID and WPA2-Personal password in hidden local prompts; never paste them into ChatGPT. No password is accepted as a command argument, written to a plaintext USB file, or placed in a PowerShell function parameter/log by this implementation. The plaintext is processed in memory; compromised endpoints, debuggers and memory/pagefile capture are outside this guarantee.

Optional Windows testing uses the Native Wi-Fi API and an in-memory temporary WPA2/AES profile. It requires exactly one Wi-Fi adapter and explicit `TEST` approval because it can temporarily interrupt Wi-Fi. It does not write XML or create a persistent Windows profile. It requires authentication on that temporary profile, then waits for the previous saved profile to reconnect. With no adapter, multiple adapters or unsupported temporary profiles, skip this optional test and let Debian test the actual adapter. Do not interpret an existing saved connection as proof that newly typed credentials work.

The output is `wifi-<nonce>.age`. The password is encrypted by maintained age, not custom cryptography. Record the **ciphertext SHA256** shown on Windows and compare it at Debian. Recipient encryption alone does not authenticate the sender; this independent hash plus console approval prevents silently substituting a different capsule. Pairing requests expire and are consumed after successful commit.

Supported now: WPA2-Personal and WPA2-compatible mixed networks. Pure WPA3, enterprise/EAP and passphrases outside 8–63 printable ASCII characters need a separately supported workflow.

## 6. Apply at the Debian console, with automatic rollback

Return the USB to Debian. `inspect.sh` lists wireless interface names and hardware IDs without printing network config/passwords. Use the detected interface name, not an invented name:

```sh
sudo law-usb apply --capsule /media/usb/wifi-NONCE.age --sha256 HASH_SHOWN_ON_WINDOWS --interface ACTUAL_INTERFACE
```

The installed controller checks the exact ciphertext bytes, decrypts in memory, validates the private pairing state, displays an escaped SSID and a concrete file/owner plan, and requires `APPLY`. NetworkManager-owned interfaces use a new private profile; unmanaged ifupdown interfaces use a new included drop-in. Existing ifupdown definitions, conflicting managers and systemd-networkd configurations are preserved and block automatic migration. Missing firmware is a hardware prerequisite, not something a password file can fix.

A root-owned rollback worker and 180-second systemd timer are installed **before** network files change. Password/derived PSK and backups are kept only in mode-0600 files on Debian. The WPA2-derived PSK is credential-equivalent: do not share it. Debian must confirm the selected authenticated connection and a global IPv4 address. Test access from Windows, then type `KEEP` before timeout. Otherwise files are restored and disconnection is requested. Physical network deactivation is not verified by the file-restore tests; keep console access. Association/IP does not by itself prove internet, DNS, firewall policy or SSH access.

Read-only transaction status and explicit local recovery:

```sh
sudo law-usb status
sudo law-usb recover --transaction NONCE
```

Recovery restores that transaction's saved files after `ROLLBACK` approval; it can replace later edits to those same files. Backups never leave Debian. Keep console access during the first physical test.

## Tested evidence and known limits

Debian 12/13 amd64 package signature chains and offline installation/repetition are tested in disposable containers; no-network containers are not hardware/boot tests. PowerShell/C# compilation and cross-language encryption can be checked on Linux PowerShell; this is **not** native Windows Wi-Fi qualification. Physical USB boot, Secure Boot, real Wi-Fi adapters/firmware and network rollback require a powered-on test machine.

The cloud currently blocks `cdimage.debian.org`; no ISO is included, claimed verified or claimed boot-tested. Download/verification can be performed on Windows through the official sites. Firmware is not silently guessed or bundled: use the actual adapter IDs and authenticated Debian non-free-firmware packages/media as needed.

Developer commands from a checkout with Docker and the project venv:

```sh
workshop usb bundle --debian 12 --output /workspace/artifacts/law-usb/debian12-amd64
workshop usb bundle --debian 13 --output /workspace/artifacts/law-usb/debian13-amd64
workshop usb pack --packages /workspace/artifacts/law-usb --age-archive /path/to/age-v1.3.2-windows-amd64.zip --output /workspace/artifacts/LAW-USB-Tools.zip
```

The pack command re-verifies the bundles, pins the Windows age archive/executable hashes against the upstream release and Microsoft winget manifest, includes age's license, and emits a data ZIP plus SHA256. Large package/executable artifacts stay outside Git. Debian packages retain their embedded copyright/license files and corresponding source is available from Debian's repositories. This is a local operator bundle, not a publicly published release or a complete deployment platform.
