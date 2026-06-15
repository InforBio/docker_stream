# STREAM Analysis Environment — Docker Setup

This Docker image provides a pre-configured Python 3.7 environment (`stream_env`) with [STREAM](https://github.com/pinellolab/STREAM) and all required dependencies, ready to use from the terminal.

> **Platform:** This guide targets macOS. Linux users can follow the same steps but do not need the `--platform linux/amd64` flag. Windows users need Docker Desktop with WSL2 and should adapt volume paths accordingly.

## Prerequisites

- [Docker Desktop](https://docs.docker.com/desktop/setup/install/mac-install/) installed and running on your Mac

## What you need

Either:

- The Docker image file `inforbio-stream.tar.gz` provided by your colleague, **or**
- An internet connection to pull the image from Docker Hub

And:

- This `README.md`

---

## Step 1 — Load the Docker image

**Option 1a — from the `.tar.gz` file:**

```sh
gunzip -c ~/Downloads/inforbio-stream.tar.gz | docker load
```

> Adjust the path if you saved the file elsewhere.

**Option 1b — from Docker Hub (requires internet):**

```sh
docker pull --platform linux/amd64 lijiaoning/inforbio-stream:latest
docker tag lijiaoning/inforbio-stream:latest inforbio-stream
```
> `--platform linux/amd64` is required on Apple Silicon Macs (M1/M2/M3) because the image was built for Intel architecture. Do not remove this flag.

The `docker tag` line gives the image the short name `inforbio-stream` used in the rest of this guide.

Verify the image is available:

```sh
docker images
```

You should see `inforbio-stream` in the list.

---

## Step 2 — Start the container

Run the container and mount a local folder so you can access your data and save results:

```sh
docker run --name stream_container --platform linux/amd64 -it \
    -v /path/to/your/data:/workspace \
    inforbio-stream /bin/bash
```

Replace `/path/to/your/data` with the actual path to the folder on your Mac that contains your data files. For example:

```sh
docker run --name stream_container --platform linux/amd64 -it \
    -v ~/Desktop/my_analysis:/workspace \
    inforbio-stream /bin/bash
```

> `-it` keeps the terminal interactive so you can type commands inside the container.

This opens a bash shell inside the container. Your local folder will be accessible at `/workspace` inside the container.

---

## Step 3 — Activate the STREAM environment

Every time you open a shell inside the container, run both commands:

```sh
source /opt/miniconda/etc/profile.d/conda.sh
conda activate stream_env
```

Your prompt will change to `(stream_env) root@...`, confirming the environment is active.

> Both lines are required. `source` initialises conda for the current shell session; `conda activate` then switches to the `stream_env` environment.

---

## Step 4 — Run Python

Start an interactive Python session:

```sh
python
```

Or run a script:

```sh
python /workspace/my_script.py
```

---

## Pause and resume

When you are done for the day, **exit the container** by typing `exit` in the bash shell, then stop it:

```sh
docker stop stream_container
```

The container is preserved with everything intact (files created, changes made inside the container's filesystem).

To resume the next day:

```sh
docker start -ai stream_container
```

> `-ai` reattaches the terminal (`-a`) and keeps it interactive (`-i`).

This drops you back into the bash shell. Re-run the two activation commands from Step 3.

To check whether the container is stopped but still exists:

```sh
docker ps -a
```

---

## Open a second terminal window in a running container

If you need a second terminal while the container is already running:

```sh
docker exec -it stream_container /bin/bash
```

Then run the two activation commands from Step 3.

---

## Remove the container when no longer needed

This deletes the container (not the image). Your data in the mounted folder is unaffected.

```sh
docker rm stream_container
```

To also remove the image:

```sh
docker rmi inforbio-stream
```

---

## Installing new Python packages

### Option A — Install by hand (fast but fragile)

Use `conda install` or `pip install` directly inside the running container. Changes survive `docker stop/start` but are lost on `docker rm` (remove container). Fine if you never need to recreate the container.

### Option B — Install by hand and save a snapshot (recommended)

Install packages normally inside the container (after activating `stream_env`):

```sh
conda install -c conda-forge <package-name>
# or
pip install <package-name>
```

Then, from a **new terminal on your Mac** (not inside the container), save the current state of the container as a new image:

```sh
docker commit stream_container inforbio-stream-custom
```

> Do this before ever running `docker rm`. Packages installed by hand are lost if the container is deleted without committing first.

From now on, use `inforbio-stream-custom` as your image name when running a new container:

```sh
docker run --name stream_container --platform linux/amd64 -it \
    -v ~/Desktop/my_analysis:/workspace \
    inforbio-stream-custom /bin/bash
```

You can commit again after each new installation to keep the snapshot up to date.

### Option C — Rebuild the image from source (for bigger changes)

Use this if you need to make structural changes to the environment (*e.g.*, adding a package that requires specific conda channels or version pinning). You will need two extra files from your colleague: `Dockerfile` and `env_STREAM.yml`.

> This requires internet access — Docker will download the base image (`lijiaoning/inforbio:4.5.2`) from Docker Hub during the build.

1. Place both files in the same folder, *e.g.* `~/Downloads/stream-rebuild/`:

   ```text
   Downloads/
     └── stream-rebuild/
         ├── Dockerfile
         └── env_STREAM.yml
   ```

2. Edit `env_STREAM.yml` to add your packages under `dependencies`:

   ```yaml
   dependencies:
     - python=3.7
     - stream=1.0
     - <your-new-package>
     ...
   ```

3. Build the new image (this takes several minutes):

   ```sh
   cd ~/Downloads/stream-rebuild
   docker build --platform linux/amd64 -t inforbio-stream-custom \
       -f Dockerfile .
   ```

4. Run a container from the new image as in Step 2 of this guide, replacing `inforbio-stream` with `inforbio-stream-custom`.
