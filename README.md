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

## Full release pipeline

The **Build All Lyd Ark Images and Installer ISO** workflow in
[GitHub Actions](https://github.com/lydiaperspective/lyd-ark-fork/actions/workflows/build-all.yml)
runs the complete release sequence from one manual dispatch:

1. Builds and publishes the Alga installer package from `lyd-agka`.
2. Runs the full image payload build in `lyd-ark-image`, publishing both
   userspace bases, the standard/Apex/server kernel layers, and all seven
   final bootc variants:
   - `intel-modern`
   - `intel-modern-apex`
   - `ark-nvidia-open`
   - `ark-apex-nvidia-open`
   - `ark-nvidia-580`
   - `ark-apex-nvidia-580`
   - `intel3-server-lts`
3. Builds and publishes the KDE Plasma installer ISO from this repository.

Each stage waits for its remote GitHub Actions run to complete successfully
before starting the next stage. A failed or timed-out stage stops the pipeline.

### One-time GitHub secret

Because the workflow dispatches Actions runs in three separate repositories,
add a fine-grained personal access token as the repository Actions secret
`ARK_WORKFLOW_TOKEN` in `lyd-ark-fork`.

Give the token access to these repositories:

- `lyd-agka`
- `lyd-ark-image`
- `lyd-ark-fork`

Required fine-grained token permissions:

- **Actions: Read and write** — dispatch workflows and inspect their runs
- **Contents: Read-only** — identify the current `main` commit before dispatch

The individual workflows use their own repository `GITHUB_TOKEN` permissions
to publish packages, container images, and GitHub Releases. The personal token
is used only to start and monitor the workflows.

After adding the secret, open the workflow link above, choose **Run workflow**,
and select the image build runner. The default is GitHub-hosted; the self-hosted
option requires the `ark-builder` runner labels configured in
`lyd-ark-image`.
