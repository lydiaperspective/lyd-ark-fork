# Lyd Ark KDE Installer

**Lyd Ark** is an Arch-based, image-oriented Linux project built around
[bootc](https://github.com/containers/bootc), with KDE Plasma as the desktop
environment. This repository builds the bootable KDE Plasma live installer
ISO and publishes it as a GitHub release.

## What this repository builds

- A bootable x86_64 live ISO using Archiso
- The Lyd Ark KDE Plasma live environment
- The Alga graphical installer package
- Release assets with SHA-256 verification
- Automatic splitting for ISOs larger than the 1900 MiB release-asset threshold

The installer uses the Lyd Ark image builder's published desktop base image
and the current Alga package release. The selected Lyd Ark bootc image variant
is installed by Alga.

## Build locally

Requirements:

- Podman
- `wget`, `curl`, `jq`, and `gh`
- Root privileges for the Archiso build
- Sufficient free disk space for the image build and ISO

Build the live ISO:

```bash
sudo podman run --rm --privileged \
  -v "$(pwd):/work" \
  -w /work docker.io/archlinux:latest \
  bash /work/.github/workflows/build_iso.sh
```

The generated ISO is placed in `out/`. The GitHub Actions workflow renames
the generated file to:

```text
lyd-ark-kde-installer.iso
```

## GitHub releases

The workflow publishes the ISO as a single file when it is at or below
1900 MiB. Larger ISOs are split into numbered parts. Every release includes
`SHA256SUMS`; split releases also include `recombine-iso.sh`.

For a single-file release, verify the download with:

```bash
sha256sum -c SHA256SUMS
```

For a split release, download all files named
`lyd-ark-kde-installer.iso.partNNN.part`, along with `SHA256SUMS` and
`recombine-iso.sh`, into the same directory. Then run:

```bash
chmod +x recombine-iso.sh
./recombine-iso.sh
sha256sum -c SHA256SUMS
```

The recombination script also verifies the reconstructed ISO before
reporting success.

## Related repositories

- [lyd-ark-image](https://github.com/lydiaperspective/lyd-ark-image) —
  builds and publishes the Lyd Ark bootc images
- [lyd-agka](https://github.com/lydiaperspective/lyd-agka) —
  Lyd Ark's Alga graphical installer fork
- [lyd-ark-themes](https://github.com/lydiaperspective/lyd-ark-themes) —
  KDE theme development for Lyd Ark

## Project status

Lyd Ark is under active development. Treat installer images as test builds
until the relevant image-build, ISO-build, and hardware-install tests have
passed.
