# Security Policy — AllTools

## Overview

AllTools is a **local desktop application**. It makes no network requests and sends no data to any external server, cloud service, or third party. All file operations run entirely on the user's machine.

## Scope

| Area | Status |
|---|---|
| Network communication | ✅ None — fully offline |
| File operations | ✅ Local only, user-selected paths |
| Input validation | ✅ Enforced on all tool parameters |
| Password handling | ✅ PDF passwords are passed directly to PyMuPDF's AES-256 engine and never stored |
| Third-party telemetry | ✅ None |

## Input Validation

All API inputs are validated before any file operation:
- **Numeric parameters** (width, height, degrees, scale, duration, page numbers) must be valid numbers within safe ranges.
- **File paths** are validated to prevent path traversal attacks (`../`, absolute redirects).
- **File extensions** are whitelisted per tool — e.g. image tools only accept `.png`, `.jpg`, `.webp`, `.bmp`, `.gif`; video tools only accept `.mp4`, `.mov`, `.avi`, `.mkv`.

## Reporting a Vulnerability

If you discover a security issue, please open a **GitHub Issue** with the label `security` or contact the author directly.

**Do not** include exploit code or sensitive data in public issue reports.

## Author

**Ali Qureshi**  
MIT License — see [LICENSE](LICENSE)
