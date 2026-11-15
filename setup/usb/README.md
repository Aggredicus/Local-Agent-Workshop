# One USB: Windows setup, Debian installation, safe Wi-Fi recovery

Use a **32 GB or larger** USB with Ventoy's exFAT/NTFS data partition. ThinkCentre1 keeps its existing Windows 11 installation. The requested fresh-install path installs Debian + LAW on ThinkCentre2 after you confirm the destination disk. The optional recovery path below preserves an existing Debian installation.

This tools ZIP **is not bootable by itself and contains no Debian installer ISO**. It supplies Windows tools plus real offline recovery packages. Menu option **2** downloads the separately built, verified custom LAW ISO to Desktop; option **3** copies it and the LAW tools to an already prepared Ventoy USB. Installation still requires you to select and confirm the target disk. No Windows tool here formats a disk. Each completed or failed action returns to the menu; **0** exits.

## 1. Prepare on Windows — no WSL, Git or Python required

1. Download the prepared LAW USB tools ZIP and its SHA256. **Compare the hash with the value supplied independently alongside the download**, before executing anything:

   ```powershell
   Get-FileHash -Algorithm SHA256 -LiteralPath .\LAW-USB-Tools.zip
   Expand-Archive -LiteralPath .\LAW-USB-Tools.zip -DestinationPath .\LAW-USB-Tools
   ```

   A checksum file on the same untrusted USB is not an independent trust anchor. Keep the verified extracted folder on Windows; returning USB files must never replace this trusted code.
2. Extract the ZIP **anywhere you can write**, open its `LAW` folder, and double-click `START-USB.cmd`. After verifying the ZIP and reviewing the scripts, press **Y** at its approval prompt. The launcher locates scripts relative to itself; it does not assume Downloads or depend on your terminal's current folder. No commands need to be pasted into PowerShell.
3. Approval starts Windows PowerShell with **RemoteSigned for that process only** and removes the downloaded-file block from exactly `Start-USB.ps1`, `Prepare-USB.ps1` and `Wifi-Capsule.ps1`. The file unblock persists for those files, but your saved execution policies are not changed. Closing the process ends its temporary policy. Declining starts no scripts and changes no files. Administrator-enforced policy still applies; contact your administrator if it requires signed scripts or prohibits them. No `Bypass` or administrator elevation is used.
4. Choose **1** to stage the credential-entry tools and launcher into `%LOCALAPPDATA%\LocalAgentWorkshop\USBTools`. The new per-user folder has restricted ACLs. The age executable is additionally checked against a pinned SHA256 before any credentials are requested. Keep this local installation for later USB round trips. Existing staged installations are preserved; review/preserve them before an upgrade. Windows PowerShell 5.1 is the supported target; the launcher's automated Windows tests do not qualify real Wi-Fi or hardware behavior.

**Updating an earlier staged copy:** close the tools, open `%LOCALAPPDATA%\LocalAgentWorkshop` in File Explorer, and rename `USBTools` to an unused backup name such as `USBTools-previous`. Run the launcher from the newly verified ZIP and choose **1** again. Keep the old folder until the new tools are verified. This preserves your existing files and stages the corrected Windows framework references; do not replace local code with files from a returning USB.

## 2. Make the same USB boot Debian

1. Obtain Ventoy only through its [official download page](https://www.ventoy.net/en/download.html) and follow its integrity-verification instructions. Run its Windows utility yourself. Select the USB by its capacity/device identity and approve initialization. **Initial installation erases that selected USB.** Back up its existing contents first. This is separate from copying LAW files.
2. Choose **2** in START-USB to download **LAW-Debian-13.7.0-amd64.iso** from this repository's newest tested ISO release. Press Enter for Desktop, or enter another existing destination folder. The downloader checks the published SHA256 before completing the file; existing files are preserved. Build/source/package/VM evidence is attached to the release. See [the ISO build/install guide](../iso/README.md) for customization and the exact qualification limits.
3. Choose **3** from the original verified tools ZIP. Select the Ventoy DATA root (such as `E:\`) and the downloaded ISO (Enter uses Desktop). It checks the ISO and manifest-listed LAW files, copies a new LAW folder plus ISO, then checks the USB copies. Existing LAW/ISO files are preserved. No private key or plaintext credential belongs on USB.
4. Boot ThinkCentre2 using its firmware boot menu. Select the LAW ISO, then **LAW offline Debian + rootless Docker**. Select the destination disk, confirm partition writes, and create your normal account. Packages are included for offline installation. After reboot, the LAW CLI, Wi-Fi controller and rootless Docker are already installed; skip recovery-package/controller installation below and continue at section 4.
5. Physical USB boot, Secure Boot and firmware still need testing on your machine. Follow Ventoy's official Secure Boot procedure and review any key-enrollment request. These scripts do not disable Secure Boot or enroll keys.

**Existing-system recovery:** if you choose to keep the current Debian installation instead, boot it normally and use sections 3–6. Do not launch the fresh installer for that path.

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

Return the USB to Windows. Open `%LOCALAPPDATA%\LocalAgentWorkshop\USBTools`, run its **locally staged** `START-USB.cmd`, approve startup, then choose **4**. Use this trusted local installation for every round trip. You can also open that launcher from PowerShell:

```powershell
& "$env:LOCALAPPDATA\LocalAgentWorkshop\USBTools\START-USB.cmd"
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

Debian 12/13 amd64 package signature chains and offline installation/repetition are tested in disposable containers; no-network containers are not hardware/boot tests. Native Windows PowerShell 5.1 tests cover startup, private staging ACLs in a disposable child profile, preservation of existing tools, C# compilation and synthetic UTF-8 credential encryption/decryption using the pinned Windows age executable. The staging test changes no real user profile, and the crypto test invokes no Wi-Fi API. Physical USB boot, Secure Boot, real Wi-Fi adapters/firmware, machine-specific Windows policy/permissions and network rollback require a powered-on test machine.

The cloud workspace blocks `cdimage.debian.org`; the GitHub ISO build runner can reach it and authenticates the official netinst before remastering. The ISO is a separate download, not inside the tools ZIP. Included Debian installer firmware follows Debian hardware detection; the real ThinkCentre adapter still needs testing.

Developer commands from a checkout with Docker and the project venv:

```sh
workshop usb bundle --debian 12 --output /workspace/artifacts/law-usb/debian12-amd64
workshop usb bundle --debian 13 --output /workspace/artifacts/law-usb/debian13-amd64
workshop usb pack --packages /workspace/artifacts/law-usb --age-archive /path/to/age-v1.3.2-windows-amd64.zip --output /workspace/artifacts/LAW-USB-Tools.zip
```

The pack command re-verifies the bundles, pins the Windows age archive/executable hashes against the upstream release and Microsoft winget manifest, includes age's license, and emits a data ZIP plus SHA256. Large package/executable artifacts stay outside Git. Debian packages retain their embedded copyright/license files and corresponding source is available from Debian's repositories. This is an operator test candidate, not a production release or a complete deployment platform.
