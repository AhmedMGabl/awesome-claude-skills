import pathlib, sys
path = pathlib.Path(sys.argv[1])
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"), encoding="utf-8")
print(f"Written {path.stat().st_size} bytes to {path}")
