# Repository Instructions

## Git Remotes

- `origin` is the GitHub repository.
- `space` is the Hugging Face Space.
- Push normal development commits to `origin/main`.
- Never push `main` directly to `space/main`, because the repositories use
  different `README.md` files and histories.

## README Metadata

- Keep the GitHub `README.md` free of Hugging Face YAML frontmatter.
- Keep the Hugging Face Space configuration frontmatter at the beginning of
  the `README.md` on `space/main`.
- When syncing code to Hugging Face, preserve the existing Space frontmatter
  and combine it with the body of the GitHub `README.md`.
- Do not add a GitHub Action that rewrites or synchronizes either repository.

## Hugging Face Sync

When asked to sync the application to Hugging Face:

1. Fetch both `origin` and `space`.
2. Start a temporary branch from `space/main`.
3. Copy the requested application files from `main`.
4. For `README.md`, retain the YAML frontmatter from `space/main` and append
   the frontmatter-free body from `main`.
5. Commit the sync on the temporary branch and push it to `space/main`.
6. Return to `main` and delete the temporary branch.

Do not overwrite unrelated Hugging Face-only settings or files.
