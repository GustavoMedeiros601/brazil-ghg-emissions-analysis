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
    raw = read_seeg(root)
    long = gross_long(raw)
    annual, states, sectors, allocation = aggregate_gross(long)
    pc = per_capita(states, population_2021(root))
    comparison = population_sensitivity(states, population_2021(root), population_2022(root))
    outputs = {"emissoes_co2e_gwp_ar5_1970_2021.csv":long, "emissao_anual_brasil.csv":annual,
               "emissao_estado_2021.csv":states, "emissao_setor_2021.csv":sectors,
               "emissao_per_capita_2021.csv":pc, "alocacao_emissoes_2021.csv":allocation, "sensibilidade_per_capita_2021.csv":comparison}
    outputs["emissao_uf_setor_2021.csv"] = state_sector(long)
    outputs["decomposicao_setorial_historica.csv"] = temporal_decomposition(long)
    national, states_balance, categories = gross_net(raw)
    outputs["balanco_nacional_2021.csv"] = national
    outputs["balanco_uf_2021.csv"] = states_balance
    outputs["categorias_seeg_2021.csv"] = categories
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


def population_2021(root):
    """Agrega estimativas municipais de julho/2021 e reconcilia com tabela de UFs."""
    file = Path(root) / "data/raw/estimativa_dou_2021.xls"
    municipalities = pd.read_excel(file, sheet_name="Municípios", header=1, engine="calamine")
    municipalities = municipalities.loc[municipalities.UF.isin(UFS)].copy()
    key = ["COD. UF", "COD. MUNIC"]
    require(not municipalities.duplicated(key).any(), "Municípios duplicados na população")
    municipalities["populacao"] = pd.to_numeric(municipalities["POPULAÇÃO ESTIMADA"].astype(str).str.replace(r"\(\d+\)", "", regex=True).str.replace(".", "", regex=False).str.strip(), errors="raise")
    result = municipalities.groupby("UF", as_index=False).populacao.sum().rename(columns={"UF":"Estado"})
    names = dict(zip("Rondônia|Acre|Amazonas|Roraima|Pará|Amapá|Tocantins|Maranhão|Piauí|Ceará|Rio Grande do Norte|Paraíba|Pernambuco|Alagoas|Sergipe|Bahia|Minas Gerais|Espírito Santo|Rio de Janeiro|São Paulo|Paraná|Santa Catarina|Rio Grande do Sul|Mato Grosso do Sul|Mato Grosso|Goiás|Distrito Federal".split("|"), "RO AC AM RR PA AP TO MA PI CE RN PB PE AL SE BA MG ES RJ SP PR SC RS MS MT GO DF".split()))
    official = pd.read_excel(file, sheet_name="BRASIL E UFs", header=None, engine="calamine")
    official = official.loc[official[0].isin(names)].copy()
    official["Estado"] = official[0].map(names)
    official["populacao"] = pd.to_numeric(official[2].astype(str).str.replace(r"\(\d+\)", "", regex=True).str.replace(".", "", regex=False).str.strip(), errors="raise")
    validate_population(result)
    validate_population(official)
    pd.testing.assert_series_equal(result.set_index("Estado").populacao.sort_index(), official.set_index("Estado").populacao.sort_index(), check_dtype=False)
    require(result.populacao.sum() == 213317639, "População nacional diverge da publicação de 2021")
    return result

def population_sensitivity(states, pop2021, pop2022):
    current = per_capita(states, pop2021).rename(columns={"populacao":"populacao_2021", "emissao_per_capita":"pc_2021"})
    previous = per_capita(states, pop2022).rename(columns={"populacao":"populacao_2022", "emissao_per_capita":"pc_base_2022"})
    result = current[["Estado","Emissao","populacao_2021","pc_2021"]].merge(previous[["Estado","populacao_2022","pc_base_2022"]],on="Estado",validate="one_to_one")
    result["rank_2021"] = result.pc_2021.rank(ascending=False, method="min").astype(int)
    result["rank_base_2022"] = result.pc_base_2022.rank(ascending=False, method="min").astype(int)
    result["mudanca_posicao"] = result.rank_base_2022 - result.rank_2021
    result["diferenca_percentual"] = (result.pc_2021 / result.pc_base_2022 - 1) * 100
    return result.sort_values("rank_2021")


def state_sector(long, year=YEAR):
    latest = long.loc[long.Ano.eq(year) & long.Estado.isin(UFS)].copy()
    latest[SECTOR] = latest[SECTOR].str.strip()
    grouped = latest.groupby(["Estado", SECTOR], as_index=False).Emissao.sum()
    grid = pd.MultiIndex.from_product([sorted(UFS), sorted(latest[SECTOR].unique())], names=["Estado", SECTOR])
    grouped = grouped.set_index(["Estado", SECTOR]).reindex(grid).reset_index()
    grouped["Cobertura"] = np.where(grouped.Emissao.notna(), "Registrado", "Sem registro na fonte")
    grouped["Total_UF"] = grouped.groupby("Estado").Emissao.transform("sum")
    grouped["Participacao_pct"] = grouped.Emissao / grouped.Total_UF * 100
    require((grouped.Emissao.dropna() >= 0).all(), "Participações negativas não cabem em barras 100%")
    np.testing.assert_allclose(grouped.groupby("Estado").Participacao_pct.sum(), 100, rtol=1e-12)
    return grouped.sort_values(["Estado", SECTOR])

def temporal_decomposition(long, periods=((2002,2003),(2008,2009))):
    data = long.copy()
    data[SECTOR] = data[SECTOR].str.strip()
    totals = data.groupby("Ano").Emissao.sum()
    rows = []
    for start, end in periods:
        require(start >= 1990 and end == start + 1, "Use pares anuais com cobertura comparável desde 1990")
        pivot = data.loc[data.Ano.isin([start,end])].groupby([SECTOR,"Ano"]).Emissao.sum().unstack("Ano")
        require(set(pivot.columns) == {start,end} and pivot.notna().all().all(), "Setor/ano ausente")
        part = pivot.rename(columns={start:"Emissao_inicial",end:"Emissao_final"}).reset_index()
        part["Ano_inicial"], part["Ano_final"] = start, end
        part["Diferenca"] = part.Emissao_final - part.Emissao_inicial
        part["Contribuicao_pp"] = part.Diferenca / totals.loc[start] * 100
        np.testing.assert_allclose(part.Diferenca.sum(), totals.loc[end] - totals.loc[start],rtol=1e-12,atol=1e-6)
        rows.append(part)
    return pd.concat(rows,ignore_index=True)


def gross_net(raw, year=YEAR):
    metric = raw.loc[raw["Gás"].eq(METRIC)].copy()
    require(year >= 1990 and year <= YEAR, "Balanço exige cobertura completa desde 1990")
    included = metric.loc[metric[KIND].isin(["Emissão", "Remoção"])].copy()
    require(not included.Estado.eq("BR").any(), "Agregado BR requer revisão para não duplicar componentes")
    require(included[year].notna().all() and np.isfinite(included[year]).all(), "Valor ausente no balanço")
    # A planilha já traz remoções negativas: não aplicar abs() nem subtrair novamente.
    removals = included.loc[included[KIND].eq("Remoção"),year]
    require((removals <= 0).all(), "Convenção de sinais das remoções mudou: revisar fonte")
    included["Estado"] = included.Estado.fillna("Sem alocação estadual")
    grouped = included.groupby(["Estado",KIND])[year].sum().unstack(KIND,fill_value=0)
    grouped = grouped.rename(columns={"Emissão":"Brutas", "Remoção":"Remocoes_assinadas"})
    grouped["Liquidas"] = grouped.Brutas + grouped.Remocoes_assinadas
    grouped["Ano"] = year
    national = grouped[["Brutas","Remocoes_assinadas","Liquidas"]].sum().to_frame().T
    national["Ano"] = year
    np.testing.assert_allclose(national.Liquidas, national.Brutas + national.Remocoes_assinadas,rtol=1e-12)
    categories = metric.groupby(KIND,as_index=False).agg(Registros=(year,"size"),Valor_assinado=(year,"sum"))
    categories["Incluida_no_balanco"] = categories[KIND].isin(["Emissão", "Remoção"])
    return national, grouped.reset_index(), categories
