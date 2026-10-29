"""Linux descriptor-relative file operations; no model-selected absolute paths."""

import os
import stat
from pathlib import Path

from flux.errors import Denied


def no_symlinks(path: Path) -> Path:
    path = path.absolute()
    for part in (path, *path.parents):
        if part.is_symlink():
            raise Denied("symlink_path")
    return path


def private_dir(path: Path) -> Path:
    path = no_symlinks(path)
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    info = path.stat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise Denied("private_directory_permissions")
    return path


def create_private(path: Path, data: bytes) -> None:
    no_symlinks(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    fsync_dir(path.parent)


def fsync_dir(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def private_file(path: Path) -> None:
    no_symlinks(path)
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise Denied("private_file_permissions")


class RuntimeLock:
    """Nonblocking single-instance lock; released automatically on process exit."""

    def __init__(self, root: Path):
        import fcntl

        private_dir(root)
        self.fd = os.open(root / ".runtime.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            os.close(self.fd)
            raise Denied("runtime_already_active") from exc

    def close(self) -> None:
        os.close(self.fd)
