"""Executa os notebooks em kernels novos; use após instalar requirements.txt."""
from pathlib import Path
import argparse
import os
import uuid
import nbformat
from nbclient import NotebookClient

root = Path(__file__).resolve().parents[1]
(root / ".runtime/ipython").mkdir(parents=True, exist_ok=True)
os.environ.setdefault("IPYTHONDIR", str(root / ".runtime/ipython"))
parser = argparse.ArgumentParser()
parser.add_argument("--kernel", default="python3")
parser.add_argument("--only", help="Nome exato de um notebook; por padrão executa os dois.")
args = parser.parse_args()
for path in sorted((root / "notebook").glob("*.ipynb")):
    if args.only and path.name != args.only:
        continue
    print(f"Executando {path.name}", flush=True)
    nb = nbformat.read(path, as_version=4)
    nb.nbformat_minor = 5
    for cell in nb.cells:
        cell.setdefault("id", uuid.uuid4().hex[:8])
    NotebookClient(nb, timeout=600, kernel_name=args.kernel, resources={"metadata":{"path":str(root)}}).execute()
    nbformat.validate(nb)
    nbformat.write(nb,path)
    print(f"OK: {path.name}", flush=True)
