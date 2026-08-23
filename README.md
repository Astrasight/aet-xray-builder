# AET X-Ray Builder

One-click cloud builder for **Aeternelle 3DSS Reflected Cone v1.2**.

You do **not** need Visual Studio or a compiler on your PC. GitHub Actions builds the engine on a Windows runner.

## First-time upload

Upload the contents of this folder to the root of your GitHub repository. The important files are:

- `.github/workflows/build.yml`
- `patches/0001_aet_reflected_cone_v1.2_fullsource.patch`
- `README.md`

Commit them to `main`.

## Build

1. Open your repository on GitHub.
2. Open **Actions**.
3. Select **Build AET DX11-AVX** on the left.
4. Click **Run workflow** -> **Run workflow**.
5. Wait until the job turns green.
6. Open the finished run.
7. At the bottom under **Artifacts**, download **AET-Reflected-Cone-v1.2-DX11-AVX**.
8. Extract it. You need `AnomalyDX11AVX.exe`.

The workflow pins the upstream source to:

`themrdemonized/xray-monolith@caf8a33f3b14dcdd40c34dd0ed708689151ccf9e`

It runs `git apply --check` before patching and refuses to build if the source revision is not the expected one.

## Install after build

1. Back up your current `C:\Anomaly\bin\AnomalyDX11AVX.exe`.
2. Replace it with the newly built `AnomalyDX11AVX.exe`.
3. Install the separate **AET 3DSS Reflected Cone v1.2 Shader Addon** through MO2 below 3DSS.
4. Delete `C:\Anomaly\appdata\shaders_cache`.
5. First launch with `r__aet_lens_reflect 0` to confirm the new engine starts.

Then enable the reflection path and test it in game.
