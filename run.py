import sys

if __name__ == '__main__':
    if '--desktop-scan' in sys.argv:
        import json
        from fnaf_desktop.desktop_images import scan
        from fnaf_desktop.core import settings_path
        try:
            result=scan()
            path=settings_path().parent/'desktop-scan.json'
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(json.dumps(result),encoding='utf8')
        except Exception:
            raise SystemExit(1)
    else:
        from fnaf_desktop.app import main
        raise SystemExit(main())
