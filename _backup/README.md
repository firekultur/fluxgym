# Docker assets backup

These files were moved here to use a Python-only workflow (no Docker).

Moved files:
- Dockerfile
- Dockerfile.cuda12.4
- docker-compose.yml
- .dockerignore

Restore (from repo root):

```bash
git mv _backup/Dockerfile . && git mv _backup/Dockerfile.cuda12.4 . && git mv _backup/docker-compose.yml . && git mv _backup/.dockerignore .
```

Then commit the restore.
