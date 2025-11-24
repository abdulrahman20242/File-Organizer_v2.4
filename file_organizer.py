import logging
import shutil
import threading
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Callable, List, Set
import platform
import subprocess

logger = logging.getLogger("file_organizer")
UNDO_LOG_FILE = Path("undo.log")
CATEGORIES_FILE = Path("categories.json")

DEFAULT_CATEGORIES: Dict[str, Set[str]] = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".heic", ".svg", ".ico"},
    "Videos": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg"},
    "Audio": {".mp3", ".wav", ".aac", ".ogg", ".flac", ".m4a", ".wma", ".opus"},
    "Documents": {".pdf", ".docx", ".doc", ".txt", ".pptx", ".ppt", ".xlsx", ".xls", ".odt", ".csv", ".rtf", ".tex"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"},
    "Code": {".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h", ".json", ".xml", ".yaml", ".yml"},
    "Executables": {".exe", ".msi", ".apk", ".appimage", ".dmg", ".deb", ".rpm"},
    "Others": set(),
}


def load_categories() -> Dict[str, Set[str]]:
    """Loads categories from categories.json, creates it if it doesn't exist."""
    if not CATEGORIES_FILE.exists():
        try:
            with open(CATEGORIES_FILE, "w", encoding="utf-8") as f:
                json.dump({k: list(v) for k, v in DEFAULT_CATEGORIES.items()}, f, indent=2)
            logger.info(f"Created default categories file: {CATEGORIES_FILE}")
            return DEFAULT_CATEGORIES.copy()
        except IOError as e:
            logger.error(f"Could not create default categories file: {e}")
            return DEFAULT_CATEGORIES.copy()
    
    try:
        with open(CATEGORIES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            categories = {k: set(v) for k, v in data.items()}
            
            # التأكد من وجود فئة Others دائماً
            if "Others" not in categories:
                categories["Others"] = set()
            
            return categories
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to load categories file, falling back to defaults: {e}")
        return DEFAULT_CATEGORIES.copy()


def build_ext_index(categories: Dict[str, Set[str]]) -> Dict[str, str]:
    """Builds a mapping from file extension to category name with duplicate detection."""
    idx: Dict[str, str] = {}
    duplicates: List[str] = []
    
    for cat, exts in categories.items():
        for e in exts:
            if e:
                e_lower = e.lower()
                if e_lower in idx:
                    duplicates.append(f"{e_lower} in both '{idx[e_lower]}' and '{cat}'")
                else:
                    idx[e_lower] = cat
    
    if duplicates:
        logger.warning("Duplicate extensions detected (using first occurrence):\n" + "\n".join(duplicates))
    
    return idx


def unique_path(path: Path) -> Path:
    """Generates a unique path by appending (1), (2), etc."""
    if not path.exists():
        return path
    
    i = 1
    stem, suffix = path.stem, path.suffix
    parent = path.parent
    
    while True:
        candidate = parent / f"{stem} ({i}){suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def resolve_conflict(destination: Path, conflict_policy: str) -> Optional[Path]:
    """Resolves file conflicts based on policy."""
    if not destination.exists():
        return destination
    
    if conflict_policy == "skip":
        logger.debug(f"Skipping existing file: {destination}")
        return None
    elif conflict_policy == "overwrite":
        try:
            if destination.exists():
                if destination.is_dir():
                    shutil.rmtree(destination)
                    logger.debug(f"Removed existing directory: {destination}")
                else:
                    destination.unlink(missing_ok=True)
                    logger.debug(f"Removed existing file: {destination}")
        except OSError as e:
            logger.warning(f"Could not remove existing file for overwrite: {destination} ({e})")
        return destination
    elif conflict_policy == "rename":
        new_path = unique_path(destination)
        logger.debug(f"Renamed to avoid conflict: {destination} -> {new_path}")
        return new_path
    else:
        raise ValueError(f"Unknown conflict policy: {conflict_policy}")


def log_undo_operation(action: str, src: Path, dst: Path):
    """Logs a successful file transfer for potential rollback."""
    try:
        with open(UNDO_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{action.upper()}|{src.resolve()}|{dst.resolve()}\n")
    except IOError as e:
        logger.error(f"Could not write to undo log: {e}")


def do_transfer(src: Path, dst: Path, action: str, dry_run: bool) -> bool:
    """Performs the file transfer with error handling."""
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        if dry_run:
            logger.info(f"[DRY-RUN] {action.upper()}: {src} -> {dst}")
            return True
        
        if action == "move":
            shutil.move(str(src), str(dst))
        elif action == "copy":
            shutil.copy2(str(src), str(dst))
        else:
            raise ValueError(f"Unknown action: {action}")
        
        logger.info(f"{action.upper()} {src} -> {dst}")
        log_undo_operation(action, src, dst)
        return True
    
    except PermissionError as e:
        logger.error(f"Permission denied: {src} - {e}")
        return False
    except shutil.Error as e:
        logger.error(f"Failed to {action} {src}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during {action} of {src}: {e}")
        return False


def organize_by_type(file: Path, dest_root: Path, **kwargs) -> Optional[bool]:
    """Organizes file by extension category."""
    ext_index = kwargs.get("ext_index", {})
    skip_unknown = kwargs.get("skip_unknown", False)
    
    file_ext = file.suffix.lower()
    cat = ext_index.get(file_ext)
    
    # إذا الامتداد غير مصنف
    if cat is None:
        if skip_unknown:
            # تخطي الملف
            logger.info(f"SKIPPED (uncategorized): {file.name}")
            return None
        else:
            # نقله لـ Others
            cat = "Others"
    
    dest_file = dest_root / cat / file.name
    final_dest = resolve_conflict(dest_file, kwargs['conflict_policy'])
    if final_dest is None:
        return None
    return do_transfer(file, final_dest, kwargs['action'], kwargs['dry_run'])


def organize_by_name(file: Path, dest_root: Path, **kwargs) -> Optional[bool]:
    """Organizes file into folder named after file stem."""
    dest_file = dest_root / file.stem / file.name
    final_dest = resolve_conflict(dest_file, kwargs['conflict_policy'])
    if final_dest is None:
        return None
    return do_transfer(file, final_dest, kwargs['action'], kwargs['dry_run'])


def organize_by_date(file: Path, dest_root: Path, **kwargs) -> Optional[bool]:
    """Organizes file by year and month (YYYY/MM-MonthName)."""
    try:
        m_time = file.stat().st_mtime
        date = datetime.fromtimestamp(m_time)
        dest_dir = dest_root / str(date.year) / f"{date.month:02d}-{date.strftime('%B')}"
        dest_file = dest_dir / file.name
        final_dest = resolve_conflict(dest_file, kwargs['conflict_policy'])
        if final_dest is None:
            return None
        return do_transfer(file, final_dest, kwargs['action'], kwargs['dry_run'])
    except OSError as e:
        logger.error(f"Could not access file metadata for {file.name}: {e}")
        return False
    except Exception as e:
        logger.error(f"Could not get date for {file.name}: {e}")
        return False


def organize_by_day(file: Path, dest_root: Path, **kwargs) -> Optional[bool]:
    """Organizes files into YYYY/MM/DD structure."""
    try:
        m_time = file.stat().st_mtime
        date = datetime.fromtimestamp(m_time)
        dest_dir = dest_root / str(date.year) / f"{date.month:02d}" / f"{date.day:02d}"
        dest_file = dest_dir / file.name
        final_dest = resolve_conflict(dest_file, kwargs['conflict_policy'])
        if final_dest is None:
            return None
        return do_transfer(file, final_dest, kwargs['action'], kwargs['dry_run'])
    except OSError as e:
        logger.error(f"Could not access file metadata for {file.name}: {e}")
        return False
    except Exception as e:
        logger.error(f"Could not get date for {file.name}: {e}")
        return False


def organize_by_size(file: Path, dest_root: Path, **kwargs) -> Optional[bool]:
    """Organizes file by size category."""
    try:
        size_mb = file.stat().st_size / (1024 * 1024)
        if size_mb < 1:
            cat = "Small (Under 1MB)"
        elif size_mb < 100:
            cat = "Medium (1-100MB)"
        else:
            cat = "Large (Over 100MB)"
        dest_file = dest_root / cat / file.name
        final_dest = resolve_conflict(dest_file, kwargs['conflict_policy'])
        if final_dest is None:
            return None
        return do_transfer(file, final_dest, kwargs['action'], kwargs['dry_run'])
    except OSError as e:
        logger.error(f"Could not get size for {file.name}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error processing {file.name}: {e}")
        return False


def organize_by_first_letter(file: Path, dest_root: Path, **kwargs) -> Optional[bool]:
    """Organizes file by first letter of filename."""
    first_letter = file.stem[0].upper() if file.stem else "#"
    cat = first_letter if first_letter.isalpha() else "#"
    dest_file = dest_root / cat / file.name
    final_dest = resolve_conflict(dest_file, kwargs['conflict_policy'])
    if final_dest is None:
        return None
    return do_transfer(file, final_dest, kwargs['action'], kwargs['dry_run'])


ORGANIZERS = {
    "type": organize_by_type,
    "name": organize_by_name,
    "date": organize_by_date,
    "day": organize_by_day,
    "size": organize_by_size,
    "first_letter": organize_by_first_letter,
}


def list_files(source: Path, recursive: bool, exclude_dir: Optional[Path] = None) -> List[Path]:
    """Optimized file listing with early exclusion and better error handling."""
    pattern = source.rglob("*") if recursive else source.glob("*")
    files: List[Path] = []
    exclude_resolved = exclude_dir.resolve() if exclude_dir else None
    
    for p in pattern:
        try:
            if exclude_resolved:
                try:
                    p_resolved = p.resolve()
                    if p_resolved == exclude_resolved or exclude_resolved in p_resolved.parents:
                        continue
                except (OSError, RuntimeError):
                    continue
            
            if p.is_file():
                files.append(p)
        except (OSError, PermissionError) as e:
            logger.warning(f"Could not access path {p}: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error accessing {p}: {e}")
    
    return files


def clear_undo_log():
    """Clears the undo log file."""
    if UNDO_LOG_FILE.exists():
        try:
            UNDO_LOG_FILE.unlink()
            logger.info("Undo log cleared.")
        except OSError as e:
            logger.error(f"Could not clear undo log: {e}")


def perform_undo(on_progress: Optional[Callable[[int, int], None]] = None) -> Dict[str, int]:
    """Reads the undo log and reverts the operations."""
    if not UNDO_LOG_FILE.exists():
        logger.info("No undo log found. Nothing to revert.")
        if on_progress:
            on_progress(0, 0)
        return {"total": 0, "succeeded": 0, "failed": 0}
    
    try:
        with open(UNDO_LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except IOError as e:
        logger.error(f"Could not read undo log: {e}")
        return {"total": 0, "succeeded": 0, "failed": 0}

    total = len(lines)
    succeeded = failed = 0
    
    for idx, line in enumerate(reversed(lines), start=1):
        try:
            parts = line.strip().split('|')
            if len(parts) != 3:
                logger.warning(f"Invalid undo log line: {line.strip()}")
                failed += 1
                continue
            
            action, original_src, final_dst = parts
            original_src = Path(original_src)
            final_dst = Path(final_dst)

            if final_dst.exists():
                logger.info(f"UNDO: Moving {final_dst} back to {original_src}")
                original_src.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(final_dst), str(original_src))
                succeeded += 1
            else:
                logger.warning(f"UNDO SKIP: File not found: {final_dst}")
                failed += 1
        
        except PermissionError as e:
            logger.error(f"UNDO FAILED (Permission denied): {line.strip()} - {e}")
            failed += 1
        except Exception as e:
            logger.error(f"UNDO FAILED for line: {line.strip()} - {e}")
            failed += 1
        
        if on_progress:
            on_progress(idx, total)
    
    clear_undo_log()
    return {"total": total, "succeeded": succeeded, "failed": failed}


def validate_paths(source: Path, dest: Path) -> tuple[bool, str]:
    """Validates source and destination paths for security."""
    try:
        source = source.resolve()
        dest = dest.resolve()
        
        system_dirs = []
        if platform.system() == "Windows":
            system_dirs = [
                Path.home() / "AppData",
                Path("C:/Windows"),
                Path("C:/Program Files"),
                Path("C:/Program Files (x86)"),
            ]
        elif platform.system() == "Darwin":
            system_dirs = [
                Path("/System"),
                Path("/Library"),
                Path("/usr"),
            ]
        else:
            system_dirs = [
                Path("/usr"),
                Path("/bin"),
                Path("/sbin"),
                Path("/etc"),
            ]
        
        for sys_dir in system_dirs:
            try:
                if sys_dir.exists():
                    sys_dir_resolved = sys_dir.resolve()
                    if dest == sys_dir_resolved or sys_dir_resolved in dest.parents:
                        return False, f"Cannot organize into system directory: {sys_dir}"
            except Exception:
                pass
        
        if source == dest:
            return False, "Source and destination cannot be the same."
        
        if not source.exists():
            return False, f"Source directory does not exist: {source}"
        
        if not source.is_dir():
            return False, f"Source is not a directory: {source}"
        
        return True, ""
    
    except Exception as e:
        return False, f"Path validation error: {e}"


def process_directory(**kwargs) -> Dict[str, int]:
    """Main processing function with improved error handling."""
    source: Path = kwargs['source']
    dest: Path = kwargs['dest']
    mode: str = kwargs['mode']
    
    valid, error_msg = validate_paths(source, dest)
    if not valid:
        logger.error(error_msg)
        return {
            "total": 0,
            "processed": 0,
            "succeeded": 0,
            "failed": 0,
            "skipped": 0,
            "error": error_msg
        }
    
    organizer_func = ORGANIZERS.get(mode)
    if not organizer_func:
        error_msg = f"Unknown organization mode: {mode}"
        logger.error(error_msg)
        return {
            "total": 0,
            "processed": 0,
            "succeeded": 0,
            "failed": 0,
            "skipped": 0,
            "error": error_msg
        }
    
    files: List[Path] = kwargs.get('files', list_files(source, kwargs['recursive'], exclude_dir=dest))
    total = len(files)
    
    if total == 0:
        logger.info("No files found to organize.")
        return {"total": 0, "processed": 0, "succeeded": 0, "failed": 0, "skipped": 0}
    
    processed = succeeded = failed = skipped = 0
    
    categories = kwargs.get('categories', load_categories())
    ext_index = build_ext_index(categories) if mode == "type" else {}

    for idx, item in enumerate(files, start=1):
        if kwargs.get('cancel_event') and kwargs['cancel_event'].is_set():
            logger.info("Cancellation requested. Stopping...")
            break

        result = organizer_func(item, dest, ext_index=ext_index, **kwargs)
        
        processed += 1
        if result is None:
            skipped += 1
        elif result:
            succeeded += 1
        else:
            failed += 1

        if 'on_progress' in kwargs:
            kwargs['on_progress'](idx, total, item, result)

    return {
        "total": total,
        "processed": processed,
        "succeeded": succeeded,
        "failed": failed,
        "skipped": skipped
    }


def open_file_or_folder(path):
    """Opens file or folder in system default application (cross-platform)."""
    path = str(Path(path).resolve())
    try:
        if platform.system() == "Windows":
            import os
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", path], check=True)
        else:
            subprocess.run(["xdg-open", path], check=True)
        return True
    except Exception as e:
        logger.error(f"Could not open {path}: {e}")
        return False
