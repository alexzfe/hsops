---
name: add-service
description: Use when installing, adding, updating or moving a self-hosted app or container on the homeserver with Docker Compose (Immich, Jellyfin, Plex, Nextcloud, Vaultwarden and others), or when choosing which app fits a need.
---

# Add or update a service

Read `../../shared/conventions.md` (relative to this skill's directory) first and load the server's context.

## Deploy

1. **Check for conflicts.** Look in the profile's Services table for an app that already does the same job and for port clashes.
2. **Choose the app.** If the user named a need rather than an app, walk the category in `references/catalog.md` with them. If `references/apps/<app>.md` exists, read its Deploy section before going further.
3. **Fetch the upstream compose file.** The app's official docs or release page is the source of truth, because images and environment variables drift; use it instead of writing a compose file from memory.
   - On ARM, confirm the image has an arm64 build: `docker manifest inspect <image> | grep -q arm64`.
4. **Adapt the compose file to this server.**
   - **Layout:** use the profile's Layout section, which may be adopted from the existing server or chosen at setup.
   - **Secrets:** put them in `.env` with mode 600, and generate passwords with `openssl rand -base64 24`.
   - **Restarts and versions:** set `restart: unless-stopped`, and pin the image to a version tag when the app's file asks for it.
   - **Hardware acceleration,** following the profile:
     - Intel iGPU: map `/dev/dri` and add the numeric GID from `getent group render`.
     - NVIDIA: use the `deploy` GPU block.
   - **Ownership:** set PUID/PGID, or `user:`, to match the owner of the data directories.
   - **Port:** confirm the host port is free with `ss -tlnp`.
5. **Get approval.** Show the user the compose file, the `.env` with secrets masked, and the target paths. On their go-ahead, write the files and run `docker compose up -d`.
6. **Verify.** All of these must hold:
   - `docker compose ps` shows the containers running, or healthy if they have a health check.
   - The logs show no errors 30 seconds after start.
   - `curl -sI http://localhost:<port>` gets a response.
   - The user opens the app from their own device.
   
   Tell the user about first-run steps that are theirs, such as creating the admin account.
7. **Decide how it's reached.** Ask whether they need the LAN, the tailnet or the public internet, with your recommendation. Access over the LAN or the tailnet (`tailscale serve`) is fine as it is. Public access follows fixed rule 4.
8. **Record it.** Add a row to the profile's Services table, including the data that needs backing up, and add a line to `changelog.md`. If that data is irreplaceable, suggest the `backups` skill.

**Done when:** every check in step 6 passes and step 8 is written.

## Update

1. Read the release notes for every version between the current one and the target, looking for breaking changes and required migrations.
2. Back up the app's database and config.
3. Bump the tag, then run `docker compose pull && docker compose up -d`.
4. Rerun the step 6 checks and add a line to `changelog.md`.

If something breaks, roll back by restoring the previous tag and the backup.
