---
name: publish-safe-repository-files
description: Review repository files before committing or pushing so reusable public assets, templates, code, and documentation are tracked without exposing personal meeting records, sensitive data, credentials, or private generated outputs. Use when deciding what to add to Git, changing ignore rules, publishing slide assets, preparing a repository push, or correcting files that were accidentally tracked.
---

# Publish Safe Repository Files

Publish reusable repository material while keeping meeting-specific and sensitive material local.

## Classify files

Track a file only when it is both reusable and approved for repository distribution.

- Track source code, tests, generic templates, public documentation, and approved shared assets such as logos.
- Keep transcripts, summaries, attendee information, personal notes, credentials, datasets, private analysis outputs, and meeting-specific generated files ignored.
- Judge content and provenance, not the extension. A generic `.tex` template or reference `.pdf` may be reusable; a dated deck containing internal results may not be.
- Treat an unknown logo, photograph, dataset, or third-party document as unapproved until its source and redistribution status are known.

## Review before staging

1. Inspect `git status --short`, the current branch, remote, and applicable `.gitignore` rules.
2. Resolve each new or modified file to a category above. Ask the user before publishing anything whose audience, ownership, or sensitivity is unclear.
3. Inspect text for names, email addresses, access tokens, passwords, private paths, meeting records, and unpublished data. Inspect image or document metadata when it may contain author or location information.
4. Put reusable assets in a stable shared directory. Keep copies inside ignored generated directories untracked.
5. Adjust ignore rules narrowly. Unignore only the intended shared path, never an entire private artifact tree.
6. Stage explicit paths. Do not use broad staging when ignored or private material is nearby.
7. Review `git diff --cached --stat`, `git diff --cached`, and `git diff --cached --check` before committing.

## Correct an accidental publication

If a file was committed but not pushed, remove it from the commit without deleting the local copy. If it was already pushed, make a normal removal commit unless the content contains credentials, personal data, or another serious secret. For serious exposure, stop and ask before rewriting shared history; removal from the latest tree does not erase earlier commits.

## Repository convention

In this repository, track approved shared logos under `slides/assets/`. Keep dated slide directories, compiled decks, meeting records, and personal project outputs ignored. Copy shared logos into a private deck only for local compilation.
