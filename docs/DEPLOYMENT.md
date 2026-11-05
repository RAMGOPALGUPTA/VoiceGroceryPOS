# Windows Deployment

## Production process

During development, frontend and backend may run separately. In production, Electron supervises the packaged Python backend.

## Build

- Vite production frontend.
- PyInstaller backend executable, including runtime libraries and model resource paths.
- Electron Builder Windows installer.
- Bundle only ASR models with verified redistribution rights and working offline runtime.

## Data directory

Use mutable application data outside the installation folder, e.g.:

```text
%ProgramData%\VoiceGroceryPOS\
  database\
    voicegrocery.db
  backups\
  logs\
  imports\
  models\
```

Choose machine-wide/per-user install and ACL policy deliberately. Never store customer DB in Program Files or app bundle.

## Installer requirements

- Install app/runtime/model dependencies.
- Create shortcut and launch app.
- Wait for backend health.
- Show offline and readiness status.
- Preserve database, backups, printer settings and models during upgrades.
- Back up before schema migrations.
- Support printer test, backup/export, and restore.
- Do not silently delete business data during uninstall.

## Clean-machine acceptance

1. Install without Python, Node.js, or VS Code.
2. Disconnect internet.
3. Launch application.
4. Import sample workbook.
5. Create and confirm bill.
6. Print and reprint receipt.
7. Restart PC and verify persisted data.
8. Backup and restore DB.
9. Upgrade application and verify history remains.
