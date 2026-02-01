# Workflow Guide

## Repository Setup

### Cloning the Repository

```bash
git clone https://github.com/Breakthrough/opencv-python-cuda.git
cd opencv-python-cuda
```

### Adding Upstream Remote

To sync with the main `opencv/opencv-python` repository, add it as a remote:

```bash
git remote add upstream https://github.com/opencv/opencv-python.git
```

### Preventing Tag Pollution

The upstream `opencv/opencv-python` repo has numeric tags (0, 1, 2, ... 90) that will pollute your local repo during fetches. To prevent this, configure the remote to exclude tags:

```bash
git config remote.upstream.tagOpt --no-tags
git config --add remote.upstream.fetch '^refs/tags/*'
```

The `tagOpt` setting alone is sometimes not respected, so the negative refspec (`^refs/tags/*`) explicitly excludes all tags.

### Syncing with Upstream

After configuring the remote, you can sync without getting unwanted tags:

```bash
git fetch upstream
git pull --rebase upstream 4.x
```

### Removing Accidentally Fetched Tags

If you already fetched the numeric tags, remove them with:

```bash
git tag -d 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 68 70 72 74 76 78 80 82 84 86 88 90
```

---

## Triggering Builds

To trigger the Windows CUDA build workflow:

```bash
gh workflow run build_wheels_windows.yml --ref 4.x-cuda -R Breakthrough/opencv-python-cuda
```

**Important:** Always specify `-R Breakthrough/opencv-python-cuda` when using `gh` commands. This repo is a fork of `opencv/opencv-python`, and `gh` will default to the parent repository without the explicit `-R` flag.

### Build Options

| Option | Description | Default |
|--------|-------------|---------|
| `restore_build_cache` | Restore build cache from previous runs | `true` |
| `save_build_cache` | Save build cache after completion | `true` |
| `rolling_build` | Use latest commit from upstream OpenCV | `false` |

Example with options:

```bash
gh workflow run build_wheels_windows.yml --ref 4.x-cuda -R Breakthrough/opencv-python-cuda \
  -f restore_build_cache=false \
  -f save_build_cache=true
```

### Force Rebuild (No Cache)

To force a complete rebuild without using cached artifacts:

```bash
gh workflow run build_wheels_windows.yml --ref 4.x-cuda -R Breakthrough/opencv-python-cuda \
  -f restore_build_cache=false
```

---

## Monitoring Builds

List recent runs:

```bash
gh run list -R Breakthrough/opencv-python-cuda --limit 5
```

Watch a running build:

```bash
gh run watch <run-id> -R Breakthrough/opencv-python-cuda
```

View build details:

```bash
gh run view <run-id> -R Breakthrough/opencv-python-cuda
```

---

## Reference: Git Config for Remotes

After setup, your `.git/config` remote sections should look like:

```ini
[remote "origin"]
    url = https://github.com/Breakthrough/opencv-python-cuda.git
    fetch = +refs/heads/*:refs/remotes/origin/*

[remote "upstream"]
    url = https://github.com/opencv/opencv-python.git
    fetch = +refs/heads/*:refs/remotes/upstream/*
    fetch = ^refs/tags/*
    tagOpt = --no-tags
```
