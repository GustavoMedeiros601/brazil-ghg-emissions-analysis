"""Executa os notebooks em kernels novos; use após instalar requirements.txt."""
from pathlib import Path
import argparse
import os
import nbformat
from nbclient import NotebookClient

root = Path(__file__).resolve().parents[1]
os.environ.setdefault("IPYTHONDIR", str(root / ".runtime/ipython"))
parser = argparse.ArgumentParser()
parser.add_argument("--kernel", default="python3")
args = parser.parse_args()
for path in sorted((root / "notebook").glob("*.ipynb")):
    print(f"Executando {path.name}", flush=True)
    nb = nbformat.read(path, as_version=4)
    NotebookClient(nb, timeout=600, kernel_name=args.kernel, resources={"metadata":{"path":str(root)}}).execute()
    nbformat.validate(nb)
    nbformat.write(nb,path)
    print(f"OK: {path.name}", flush=True)
