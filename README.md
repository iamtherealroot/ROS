# ROS – Root Operating System 🌱

**Sei wie Root!**

ROS is a community-oriented, Linux Mint Cinnamon-based desktop distribution project, currently developed in a **private** repository.

> **Status: early development / prototype.** There is no released, validated ROS installer ISO yet. Do not use the experimental remaster scripts on production hardware.

## Vision

One installer, two modes (**Simple** and **Expert**), four selectable profiles:

| Profile | Purpose |
| --- | --- |
| Minimal | Cinnamon, Firefox, LibreOffice, Bitwarden and ROS essentials |
| IT | Minimal + WireGuard GUI, Wireshark, SSH, Git/GitHub CLI, QEMU/KVM and virt-manager |
| Gaming | Minimal + Steam, Heroic, GameMode, Vulkan and Ubisoft Connect setup assistant |
| Complete | Minimal + IT + Gaming |

Optional software belongs in **ROS Have-To**. Gaming/Complete installers will also offer optional streaming software and service presets. Media services (Spotify, Deezer, Apple Music) are optional across all profiles.

## Design

- Name: **ROS**; tagline: **Sei wie Root!**
- Roots-and-shield emblem, black/mint-green look, matching wallpaper
- Cinnamon desktop, split-layout login concept, Plymouth splash concept
- **Terminator** labeled “Terminal”, searchable via `cmd` on every profile
- German default with English language support
- LUKS2-capable setup, password-based unlock, separate desktop login

## Planned components

- `apps/ros-wireguard/` – user-friendly NetworkManager WireGuard profile management
- `apps/ros-have-to/` – optional software catalog
- `apps/ros-welcome/` – first-run experience
- `apps/ros-update/` – ROS-specific updates alongside Mint security updates
- `installer/` – profile selection and simple/expert installation workflows
- `branding/` – root/shield logo, wallpapers, Plymouth, LightDM and sounds
- `iso/` – repeatable ISO build and validation

## Development workflow

1. Develop and verify features inside a **Hyper-V ROS-Development** Linux Mint VM.
2. Capture tested changes as reproducible source/packages in Git.
3. Build from an **authentic, signature-verified Linux Mint 22.3 Cinnamon ISO** in the separate build VM.
4. Test the resulting ISO in a fresh ROS-Test VM, including UEFI, LUKS, boot, installer, profile selection, updates and rollback.
5. Publish only validated releases, with checksums and installation instructions.

The existing ROS-1.0.0-dev ZIP is an **experimental prototype** and is not yet equivalent to this specification.

## Open source roadmap

ROS is intended for the community. License selection, third-party redistribution rights, Linux Mint trademarks and attribution must be reviewed before changing this repository to public. Do not commit VPN private keys, passwords, credentials, machine IDs or personal configuration.

## Project links

- [Development roadmap](docs/ROADMAP.md)
- [Project specification](docs/SPECIFICATION.md)
