#!/usr/bin/env bash
set -euo pipefail

REMOTE="origin"
BRANCH="master"
MESSAGE="update"
YES=0

usage() {
  cat <<'USAGE'
Usage:
  ./scripts/force-push-master.sh [--yes] [-m "commit message"]

What it does:
  Creates one new root commit from the current working tree and force-pushes it
  to origin/master, so the remote master branch no longer points to old history.

Options:
  -m, --message TEXT   Commit message for the new single commit. Default: update
  -r, --remote NAME    Remote name. Default: origin
  -b, --branch NAME    Branch name. Default: master
  -y, --yes            Skip confirmation prompt
  -h, --help           Show this help
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    -m|--message)
      [ "${2:-}" ] || { echo "Missing value for $1" >&2; exit 2; }
      MESSAGE="$2"
      shift 2
      ;;
    -r|--remote)
      [ "${2:-}" ] || { echo "Missing value for $1" >&2; exit 2; }
      REMOTE="$2"
      shift 2
      ;;
    -b|--branch)
      [ "${2:-}" ] || { echo "Missing value for $1" >&2; exit 2; }
      BRANCH="$2"
      shift 2
      ;;
    -y|--yes)
      YES=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      MESSAGE="$1"
      shift
      ;;
  esac
done

git rev-parse --is-inside-work-tree >/dev/null
git check-ref-format --branch "$BRANCH" >/dev/null
git remote get-url "$REMOTE" >/dev/null

CURRENT_BRANCH="$(git branch --show-current)"
if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
  echo "Current branch is '$CURRENT_BRANCH', but target branch is '$BRANCH'." >&2
  echo "Switch to '$BRANCH' first, then run this script." >&2
  exit 1
fi

if git diff --name-only --diff-filter=U | grep . >/dev/null; then
  echo "Unmerged files detected. Resolve conflicts before rewriting history." >&2
  exit 1
fi

TIMESTAMP="$(date +%Y%m%d%H%M%S)"
ORIGINAL_HEAD="$(git rev-parse --verify HEAD)"
SHORT_HEAD="$(git rev-parse --short HEAD)"
TMP_BRANCH="_tmp_squash_${BRANCH}_${TIMESTAMP}_${SHORT_HEAD}"
BACKUP_BRANCH="backup/${BRANCH}-before-squash-${TIMESTAMP}"

while git show-ref --verify --quiet "refs/heads/$TMP_BRANCH"; do
  TMP_BRANCH="${TMP_BRANCH}_$RANDOM"
done

while git show-ref --verify --quiet "refs/heads/$BACKUP_BRANCH"; do
  BACKUP_BRANCH="${BACKUP_BRANCH}_$RANDOM"
done

cleanup() {
  set +e
  ACTIVE_BRANCH="$(git branch --show-current 2>/dev/null)"
  if [ "$ACTIVE_BRANCH" = "$TMP_BRANCH" ]; then
    git checkout "$BRANCH" >/dev/null 2>&1
  fi
  git branch -D "$TMP_BRANCH" >/dev/null 2>&1
}
trap cleanup EXIT

echo "This will rewrite '$REMOTE/$BRANCH' as one single root commit."
echo "A local backup branch will be created at '$BACKUP_BRANCH'."
echo "Commit message: $MESSAGE"

if [ "$YES" -ne 1 ]; then
  printf "Type 'rewrite %s' to continue: " "$BRANCH"
  read -r CONFIRM
  if [ "$CONFIRM" != "rewrite $BRANCH" ]; then
    echo "Aborted."
    exit 1
  fi
fi

git branch "$BACKUP_BRANCH" "$ORIGINAL_HEAD"

if [ -x "./scripts/optimize-images.sh" ]; then
  echo "Optimizing images before commit..."
  ./scripts/optimize-images.sh
fi

git checkout --orphan "$TMP_BRANCH"
git add -A
git commit -m "$MESSAGE"

NEW_COMMIT="$(git rev-parse --verify HEAD)"
git push --force "$REMOTE" "$NEW_COMMIT:refs/heads/$BRANCH"

git branch -M "$TMP_BRANCH" "$BRANCH"
git fetch "$REMOTE" "$BRANCH" >/dev/null 2>&1 || true
git branch --set-upstream-to="$REMOTE/$BRANCH" "$BRANCH" >/dev/null 2>&1 || true

trap - EXIT

echo "Done."
echo "Remote '$REMOTE/$BRANCH' now points to single commit: $(git rev-parse --short HEAD)"
echo "Local backup branch with old history: $BACKUP_BRANCH"
