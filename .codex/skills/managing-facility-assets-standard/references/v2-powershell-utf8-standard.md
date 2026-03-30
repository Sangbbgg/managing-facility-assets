# v2 PowerShell UTF-8 Standard

This document records the repository-specific terminal reading standard for Korean text when Codex is working through PowerShell.

## Rule

When a task involves reading, verifying, or copying Korean text through PowerShell:

- switch the active PowerShell session to UTF-8 before reading files
- prefer `Get-Content -Encoding UTF8` when opening text or JSON files
- treat mojibake output as a terminal decoding problem first, not as authoritative file content

Recommended session setup:

```powershell
chcp 65001 > $null
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
```

Recommended file read pattern:

```powershell
Get-Content -Encoding UTF8 <path>
```

## Intent

- prevent false conclusions caused by mojibake in PowerShell output
- keep Korean names and labels readable during seed, JSON, config, and docs work
- reduce accidental rewrites of correct Korean text based on broken terminal rendering

## Notes

- This standard affects how Codex reads terminal output, not the repository's canonical file encoding by itself.
- If a file still renders incorrectly after UTF-8 session setup and `-Encoding UTF8`, inspect the file's actual saved encoding before editing.
