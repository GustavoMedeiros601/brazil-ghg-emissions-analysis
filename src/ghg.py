"""Transformações reproduzíveis para a coleção SEEG 10 (1970–2021)."""
from pathlib import Path
import numpy as np
import pandas as pd

METRIC = "CO2e (t) GWP-AR5"
KIND = "Emissão / Remoção / Bunker"
SECTOR = "Nível 1 - Setor"
UFS = set("AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split())
SEEG_FILE = "1-SEEG10_GERAL-BR_UF_2022.10.27-FINAL-SITE.xlsx"
YEAR = 2021

def project_root(start=None):
    for candidate in (Path(start or Path.cwd()).resolve(), *Path(start or Path.cwd()).resolve().parents):
        if (candidate / "data/raw" / SEEG_FILE).is_file():
            return candidate
    raise FileNotFoundError("Execute a partir da raiz do repositório ou de notebook/.")

def require(condition, message):
    if not condition:
        raise ValueError(message)

def read_seeg(root):
    df = pd.read_excel(Path(root) / "data/raw" / SEEG_FILE, sheet_name="GEE Estados", engine="calamine")
    require({SECTOR, KIND, "Gás", "Estado", YEAR}.issubset(df.columns), "Esquema SEEG inválido")
    return df

def gross_long(raw):
    df = raw.loc[raw[KIND].eq("Emissão") & raw["Gás"].eq(METRIC)].drop(columns=KIND).copy()
    # BR é uma categoria distinta das UFs; não somar agregados a seus componentes.
    require(not df.Estado.eq("BR").any(), "Agregado BR encontrado: revisar a regra de totalização")
    require(set(df.Estado.dropna()).issubset(UFS), "UF desconhecida")
    years = [c for c in df if isinstance(c, int)]
    require(years == list(range(1970, YEAR + 1)), "Cobertura temporal inesperada")
    result = df.melt(id_vars=[c for c in df if c not in years], value_vars=years, var_name="Ano", value_name="Emissao")
    result["Ano"] = result["Ano"].astype(int)
    require(result.Emissao.notna().all() and np.isfinite(result.Emissao).all(), "Emissões ausentes ou não finitas")
    return result

def aggregate_gross(long, year=YEAR):
    annual = long.groupby("Ano", as_index=False).Emissao.sum()
    latest = long.loc[long.Ano.eq(year)].copy()
    latest[SECTOR] = latest[SECTOR].str.strip()
    states = latest.loc[latest.Estado.isin(UFS)].groupby("Estado", as_index=False).Emissao.sum().sort_values("Emissao", ascending=False)
    sectors = latest.groupby(SECTOR, as_index=False).Emissao.sum().sort_values("Emissao", ascending=False)
    allocation = latest.assign(Alocacao=np.where(latest.Estado.isin(UFS), "Alocado às UFs", "Sem alocação estadual")).groupby("Alocacao", as_index=False).Emissao.sum()
    require(set(states.Estado) == UFS and states.Estado.is_unique, "São necessárias 27 UFs únicas")
    require(np.isclose(allocation.Emissao.sum(), annual.loc[annual.Ano.eq(year), "Emissao"].iloc[0], rtol=1e-12), "Reconciliação nacional falhou")
    return annual, states, sectors, allocation

def population_2022(root):
    df = pd.read_excel(Path(root) / "data/raw/POP2022_Municipios.xls", header=1, skipfooter=34, engine="calamine")
    df = df.loc[df.UF.isin(UFS)].copy()
    df["populacao"] = pd.to_numeric(df["POPULAÇÃO"].astype(str).str.replace(r"\(\d+\)", "", regex=True).str.replace(".", "", regex=False).str.strip(), errors="raise")
    result = df.groupby("UF", as_index=False).populacao.sum().rename(columns={"UF":"Estado"})
    validate_population(result)
    return result

def validate_population(population):
    require(set(population.Estado) == UFS and population.Estado.is_unique, "População deve conter 27 UFs únicas")
    require(population.populacao.notna().all() and (population.populacao > 0).all(), "População inválida")

def per_capita(states, population):
    validate_population(population)
    result = states.merge(population, on="Estado", how="left", validate="one_to_one", indicator=True)
    require(result._merge.eq("both").all(), "UF sem população")
    result = result.drop(columns="_merge")
    result["UF"] = result.Estado
    result["emissao_per_capita"] = result.Emissao / result.populacao
    return result[["Estado", "Emissao", "UF", "populacao", "emissao_per_capita"]].sort_values("emissao_per_capita", ascending=False)

def write_csv(frame, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        try:
            pd.testing.assert_frame_equal(pd.read_csv(path), frame.reset_index(drop=True), check_dtype=False, check_exact=False, rtol=1e-12, atol=1e-7)
            return
        except AssertionError:
            pass
    frame.to_csv(path, index=False, lineterminator="\n")

def prepare(root):
    root = Path(root)
    long = gross_long(read_seeg(root))
    annual, states, sectors, allocation = aggregate_gross(long)
    pc = per_capita(states, population_2022(root))
    outputs = {"emissoes_co2e_gwp_ar5_1970_2021.csv":long, "emissao_anual_brasil.csv":annual,
               "emissao_estado_2021.csv":states, "emissao_setor_2021.csv":sectors,
               "emissao_per_capita_2021.csv":pc, "alocacao_emissoes_2021.csv":allocation}
    for name, frame in outputs.items():
        write_csv(frame, root / "data/processed" / name)
    return outputs

def validate_processed(root):
    p = Path(root) / "data/processed"
    state = pd.read_csv(p / "emissao_estado_2021.csv")
    pc = pd.read_csv(p / "emissao_per_capita_2021.csv")
    sector = pd.read_csv(p / "emissao_setor_2021.csv")
    annual = pd.read_csv(p / "emissao_anual_brasil.csv")
    allocation = pd.read_csv(p / "alocacao_emissoes_2021.csv")
    for frame, columns in [(state, {"Estado","Emissao"}), (pc, {"Estado","populacao","emissao_per_capita"}), (sector,{SECTOR,"Emissao"}), (annual,{"Ano","Emissao"})]:
        require(columns.issubset(frame.columns), "Colunas obrigatórias ausentes")
    require(state.Estado.is_unique and set(state.Estado) == UFS, "Cobertura estadual inválida")
    validate_population(pc)
    require(annual.Ano.is_unique and set(annual.Ano) == set(range(1970, 2022)), "Série anual incompleta")
    joined = pc.merge(state, on="Estado", validate="one_to_one", suffixes=("_pc","_uf"))
    np.testing.assert_allclose(joined.Emissao_pc, joined.Emissao_uf, rtol=1e-12)
    np.testing.assert_allclose(pc.emissao_per_capita, pc.Emissao / pc.populacao, rtol=1e-12)
    national = annual.loc[annual.Ano.eq(YEAR), "Emissao"].iloc[0]
    np.testing.assert_allclose(sector.Emissao.sum(), national, rtol=1e-12)
    np.testing.assert_allclose(allocation.Emissao.sum(), national, rtol=1e-12)
    np.testing.assert_allclose(state.Emissao.sum(), allocation.loc[allocation.Alocacao.eq("Alocado às UFs"), "Emissao"].iloc[0], rtol=1e-12)
    return {"ufs": len(state), "anos": len(annual), "nacional_2021_tco2e": float(national), "alocado_ufs_tco2e": float(state.Emissao.sum())}
