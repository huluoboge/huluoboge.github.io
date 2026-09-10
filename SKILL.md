# Hu Yang Homepage Maintenance Skill

Use this skill whenever updating this personal homepage, its blog, or the
open-source software list.

## Site Shape

`index.html` is deliberately minimal. It presents only:

- **About Me** — short intro, Chinese and English
- **Recent Posts** — injected at build time by CI from `blog/`
- **Focus Areas** — generic technical areas
- **Software** — open-source tools (InsightAT, FastMVS, Free PTD)
- **Contact**

The site has **no** projects section, project cards, case-study pages, resume
pages, resume PDFs, or experience timeline. These were deliberately removed.

Do not create, restore, or link to `cv/`, project case-study folders, or resume
PDFs unless the user explicitly asks. If the user does ask for project or resume
content, confirm where it should live before adding anything — do not assume it
belongs on this site.

## Core Rules

- Treat the site as the personal site of a senior 3D reconstruction engineer.
- Keep it a lightweight static site: restrained typography, white background,
  thin rules, compact layout. `styles.css` is shared with the blog template.
- **Do not invent** facts, metrics, publications, benchmark results, screenshots,
  completion status, or project limitations.
- **Do not fabricate numbers.** When no metric is available, describe mechanism
  and engineering or business impact qualitatively.
- Prefer concrete, specific technical writing over generic marketing language.

### Public vs. internal names

Publicly announced product names may be used freely — a product line the company
has launched and documented publicly is not confidential.

Do not publish device codenames, product names, repository names, or internal
project names that have **not** been publicly announced. If unsure whether a name
is public, ask before using it.

### Confidential employer material

This site is public. Do not put employer-internal material on it:

- internal performance benchmarks, timing or throughput figures, or stability
  targets
- internal performance-review ratings
- unreleased device codenames

Describe work qualitatively — mechanism plus engineering or business impact.
Scale and specification figures that the company publishes publicly on its own
site or in press material are acceptable.

## Blog

The blog lives in `blog/` as markdown under `blog/articles/`. CI builds it with
`tools/blog-renderer` and deploys via GitHub Pages
(`.github/workflows/deploy.yml`).

- `blog/index.html` does not exist in the repository — it is generated at build
  time. A link checker reports it as missing; it is not.
- `blog/template.html` uses root-absolute paths such as `/blog/static/...`.
  Those are correct for the deployed site and also look broken to a naive
  checker.
- Do not hand-edit generated HTML.
- `tools/blog-renderer` is a git submodule. Run `npm install` inside it before
  building locally.

## Verification Checklist

Before finishing an update:

- `rg` for stale or contradictory phrases such as "not complete", "missing
  benchmarks", or names of removed project pages.
- Check `git status --short` and mention only files relevant to the task.
- Verify that every referenced image and local link exists.
- Do not modify unrelated files unless explicitly asked.
