"""Executa os notebooks em kernels novos; use após instalar requirements.txt."""
from pathlib import Path
import argparse
import os
import uuid
import asyncio
import nbformat
from nbclient import NotebookClient

root = Path(__file__).resolve().parents[1]
if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
(root / ".runtime/ipython").mkdir(parents=True, exist_ok=True)
os.environ.setdefault("IPYTHONDIR", str(root / ".runtime/ipython"))
parser = argparse.ArgumentParser()
parser.add_argument("--kernel", default="python3")
parser.add_argument("--only", help="Nome exato de um notebook; por padrão executa os dois.")
parser.add_argument("--cwd", choices=["root", "notebook"], default="root", help="Pasta de execução dos kernels.")
args = parser.parse_args()
for path in sorted((root / "notebook").glob("*.ipynb")):
    if args.only and path.name != args.only:
        continue
    print(f"Executando {path.name}", flush=True)
    nb = nbformat.read(path, as_version=4)
    nb.nbformat_minor = 5
    for cell in nb.cells:
        cell.setdefault("id", uuid.uuid4().hex[:8])
    execution_dir = root if args.cwd == "root" else root / "notebook"
    NotebookClient(nb, timeout=600, kernel_name=args.kernel, resources={"metadata":{"path":str(execution_dir)}}).execute()
    nbformat.validate(nb)
    nbformat.write(nb,path)
    print(f"OK: {path.name}", flush=True)
