# Hu Yang Homepage Maintenance Skill

Use this skill whenever updating this personal homepage, resume, selected projects, case-study pages, or downloadable resume PDFs.

## Core Rules

- Treat the site as a professional portfolio for a senior 3D reconstruction and geometric vision engineer.
- Preserve the current static-site style: restrained typography, white background, thin rules, compact project cards, and case-study pages under project-specific folders.
- Use public technical names for project titles. Do not use internal product names, device code names, repository names, or zip-file names as public-facing titles unless the user explicitly asks for that branding.
- Do not invent missing facts, metrics, publications, benchmark results, screenshots, completion status, or project limitations.
- Do not imply that a project is unfinished just because supporting materials or benchmark tables were not provided.
- If source material is incomplete, write neutrally: "materials provided in this update do not include X" only when the user explicitly wants that caveat. Prefer omitting the caveat from public-facing pages.
- Use accomplishment-oriented language for completed work. Use "designed", "implemented", "delivered", "built", and "led" only when supported by the user's materials or existing site content.
- Keep Chinese and English resume content synchronized. Any resume content change must update both `cv/index.html` and `cv/en/index.html`.
- After resume changes, render both PDFs with `scripts/render-cv-pdf.sh` and verify that both PDFs are readable A4 documents.

## Resume Workflow

When updating the resume:

1. Update the Chinese HTML resume at `cv/index.html`.
2. Update the English HTML resume at `cv/en/index.html` with equivalent meaning, not a loose summary.
3. Keep the same section structure unless the user asks for a different resume strategy:
   - header/contact
   - profile / personal advantage
   - work experience
   - project experience
   - education
4. Preserve PDF download links on the resume pages:
   - Chinese page downloads `assets/huyang-cv.pdf`
   - English page downloads `assets/huyang-cv-en.pdf`
5. Render both PDFs:

```bash
scripts/render-cv-pdf.sh
```

6. Verify:
   - `pdfinfo assets/huyang-cv.pdf`
   - `pdfinfo assets/huyang-cv-en.pdf`
   - inspect first and last pages if layout changed materially

Target: A4 PDF, clean typography, no clipped text, no orphan page with only a tiny section unless unavoidable.

## Project Update Workflow

When adding a new project:

1. Read the provided material first: README, report, paper, screenshots, figures, source-code notes, or user description.
2. Identify what is factual:
   - public project title, separate from internal product/repository name
   - problem/background
   - role and personal contribution
   - implemented modules
   - production status / delivery status
   - measurable outcomes if provided
   - assets that can be shown publicly
3. Add a project card in `index.html` under `Selected Projects`, using the existing `<article class="project">` pattern.
4. Place the card at the user-requested position. If no position is requested, put stronger or newer work higher while preserving existing priority.
5. Add a case-study folder when the work deserves detail, using existing folders such as `lod-recon/`, `structure-recon/`, or `pointcloud-colorization/` as style references.
6. Use project assets locally under either:
   - `assets/projects/` for homepage thumbnails
   - `<project-folder>/figures/` for case-study figures
7. Before committing new or updated figures, optimize images for mobile browsing:

```bash
scripts/optimize-images.sh
```

Image handling defaults:
- Prefer PNG for diagrams and screenshots; prefer JPEG only for photo-like samples.
- Do not manually re-compress JPEG files repeatedly. The optimizer records each file hash in `scripts/.optimize-images-manifest.json` and skips already-processed JPEGs to avoid quality loss from multiple lossy passes.
- PNG files are resized and quantized automatically; re-running is safe only when the source image changed.
- `scripts/force-push-master.sh` runs image optimization automatically before creating the single root commit.
8. Verify all relative links and image paths.

## Public-Facing Project Writing Rules

- Prefer concise, specific technical summaries.
- Translate internal project names into reader-friendly technical descriptions, for example "Handheld LiDAR Point-Cloud Processing" instead of an internal product codename.
- State completed work as completed when the user says the project is done.
- Do not add caveats such as "benchmark data is missing", "not yet implemented", or "should be added later" unless the user explicitly asks for limitations.
- If some capability is method-supported but not confirmed as implemented, do not call it implemented. Phrase it as design capacity only if needed.
- Do not fabricate numbers. If no metrics are provided, describe mechanism and business/engineering impact qualitatively.
- Keep homepage cards short:
  - one-sentence project description
  - two contribution bullets
  - compact tech stack
  - case-study link
- Keep case-study pages structured:
  - hero
  - background/problem
  - approach
  - my contribution
  - outcome
  - representative figures

## Project Content Template

Use `docs/project-content-template.md` when asking for or organizing new project material. It is a content intake template, not a public page.

## Verification Checklist

Before finishing a homepage/project/resume update:

- `rg` for stale or contradictory phrases such as "not complete", "missing benchmarks", "should be added", or old project names.
- Check `git status --short` and mention only files relevant to the task.
- For resume updates, render both PDFs and check page count.
- For project updates, verify new links from `index.html` and all referenced images exist.
- For new or changed figures, run `scripts/optimize-images.sh` and confirm file sizes are reasonable for mobile loading.
- Do not modify unrelated files or delete user-provided source archives unless explicitly asked.
