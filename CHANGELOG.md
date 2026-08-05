## CHANGELOG

- What: Fixed acquisition image download (HTTP 400 on user-attachments) by using curl + stripping Auth on redirects; accept HTML img src attachments.
- Why: Phone uploads failed after attach; GitHub returns 400 when Accept/Auth headers are forwarded wrong.
- Files: .github/scripts/process_acquisition.py, CHANGELOG.md
