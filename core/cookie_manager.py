# core/cookie_manager.py
# Manages Netscape-format cookie files for yt-dlp.
# Place cookies in the /cookies folder:
#   cookies/youtube.txt
#   cookies/facebook.txt
#
# Cookie format (Netscape HTTP Cookie File):
#   .youtube.com  TRUE  /  TRUE  1795099330  VISITOR_INFO1_LIVE  value_here
#
# Files can be empty or missing - the system ignores them gracefully.

import os
import logging

logger = logging.getLogger(__name__)

# Resolve the cookies directory relative to this file's location
_COOKIES_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "cookies")
)

# Map platform name -> cookie filename
COOKIE_FILES = {
    "youtube": os.path.join(_COOKIES_DIR, "youtube.txt"),
    "facebook": os.path.join(_COOKIES_DIR, "facebook.txt"),
}

NETSCAPE_HEADER = "# Netscape HTTP Cookie File"


def _is_valid_cookie_file(path: str) -> bool:
    """
    Returns True only if the file exists, is non-empty,
    and looks like a valid Netscape cookie file.
    Empty files or files with only comments are treated as "no cookies".
    """
    if not os.path.isfile(path):
        return False

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except Exception as e:
        logger.warning(f"Could not read cookie file {path}: {e}")
        return False

    if not content:
        return False

    # Must contain at least one real (non-comment) cookie line
    for line in content.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            # A real cookie line has at least 7 tab-separated fields
            parts = stripped.split("\t")
            if len(parts) >= 7:
                return True

    logger.info(f"Cookie file {path} exists but contains no valid entries - skipping.")
    return False


def get_cookie_file(platform: str) -> str | None:
    """
    Returns the path to a valid cookie file for the given platform,
    or None if the file is missing/empty/invalid.

    Usage:
        cookiefile = get_cookie_file("youtube")
        if cookiefile:
            ydl_opts["cookiefile"] = cookiefile
    """
    path = COOKIE_FILES.get(platform.lower())
    if path is None:
        logger.warning(f"No cookie file configured for platform: {platform}")
        return None

    if _is_valid_cookie_file(path):
        logger.info(f"Using cookies for {platform}: {path}")
        return path

    return None


def ensure_cookie_files_exist():
    """
    Creates empty cookie files with the Netscape header if they don't exist.
    Called at startup so users know where to place their cookies.
    """
    os.makedirs(_COOKIES_DIR, exist_ok=True)
    for platform, path in COOKIE_FILES.items():
        if not os.path.exists(path):
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(f"{NETSCAPE_HEADER}\n")
                    f.write("# https://curl.haxx.se/rfc/cookie_spec.html\n")
                    f.write(f"# Add your {platform} cookies below in Netscape format.\n")
                    f.write("# Example:\n")
                    if platform == "youtube":
                        f.write(
                            "# .youtube.com\tTRUE\t/\tTRUE\t1795099330"
                            "\tVISITOR_INFO1_LIVE\tyour_value_here\n"
                        )
                    elif platform == "facebook":
                        f.write(
                            "# .facebook.com\tTRUE\t/\tTRUE\t1812632153"
                            "\tdatr\tyour_value_here\n"
                        )
                logger.info(f"Created placeholder cookie file: {path}")
            except Exception as e:
                logger.warning(f"Could not create cookie file {path}: {e}")
