"""Figuras estáticas compartilhadas pelos notebooks."""
import textwrap
import numpy as np
import matplotlib.pyplot as plt

COLORS = {"Mudança de Uso da Terra e Floresta":"#009E73", "Agropecuária":"#E69F00", "Energia":"#0072B2", "Processos Industriais":"#CC79A7", "Resíduos":"#666666"}
SHORT = {"Mudança de Uso da Terra e Floresta":"Uso da terra e florestas", "Agropecuária":"Agropecuária", "Energia":"Energia", "Processos Industriais":"Indústria", "Resíduos":"Resíduos"}

def waterfall(start, changes, end, labels, title, source):
    """changes usa deltas assinados, não magnitudes absolutas."""
    np.testing.assert_allclose(start + sum(changes), end,rtol=1e-12,atol=1e-6)
    values = np.array([start,*changes,end]) / 1e6
    fig,ax=plt.subplots(figsize=(12,6))
    current=values[0]
    upper=max(values[0],values[-1])
    lower=min(0,values[0],values[-1])
    ax.bar(0,values[0],color="#0072B2",width=.64)
    ax.text(0,values[0],f"{values[0]:,.1f}",ha="center",va="bottom",fontsize=10)
    for i,change in enumerate(values[1:-1],start=1):
        after=current+change
        ax.plot([i-1+.32,i-.32],[current,current],color=".6",linewidth=1)
        ax.bar(i,abs(change),bottom=min(current,after),color="#D55E00" if change>=0 else "#009E73",hatch="//" if change<0 else None,width=.64)
        ax.text(i,max(current,after),f"{change:+,.1f}",ha="center",va="bottom",fontsize=10)
        upper=max(upper,current,after)
        lower=min(lower,current,after)
        current=after
    ax.bar(len(values)-1,values[-1],color="#0072B2",width=.64)
    ax.text(len(values)-1,values[-1],f"{values[-1]:,.1f}",ha="center",va="bottom",fontsize=10)
    ax.set_xticks(range(len(labels)),[textwrap.fill(x,17) for x in labels])
    ax.set_ylabel("Emissões (MtCO₂e GWP-AR5)")
    ax.set_ylim(lower*1.1,upper*1.18)
    ax.set_title(title,loc="left",pad=18)
    ax.grid(axis="y",alpha=.2)
    ax.set_axisbelow(True)
    fig.text(.08,.02,source,fontsize=9)
    fig.tight_layout(rect=(0,.06,1,1))
    return fig

def state_composition(frame, sector_col):
    totals=frame.groupby("Estado").Emissao.sum().sort_values(ascending=False).head(10).sort_values()
    pivot=frame.pivot(index="Estado",columns=sector_col,values="Participacao_pct").loc[totals.index]
    if pivot.isna().any().any():
        raise ValueError("UF selecionada possui setor sem registro; não tratar ausência como zero")
    fig,ax=plt.subplots(figsize=(12,7.5))
    left=np.zeros(len(pivot))
    for sector,color in COLORS.items():
        values=pivot[sector].to_numpy()
        ax.barh(pivot.index,values,left=left,label=SHORT[sector],color=color,height=.7)
        for y,value,offset in zip(range(len(pivot)),values,left):
            if value>=9:
                ax.text(offset+value/2,y,f"{value:.0f}%",ha="center",va="center",color="black" if sector=="Agropecuária" else "white",fontsize=9)
        left+=values
    ax.set_yticks(range(len(pivot)),[f"{uf}  |  {totals[uf]/1e6:.1f} Mt" for uf in pivot.index])
    ax.set_xlim(0,100)
    ax.set_xlabel("Participação no total bruto da UF (%)")
    ax.set_title("Perfis setoriais dos dez maiores emissores — 2021",loc="left",pad=16)
    ax.legend(loc="upper center",bbox_to_anchor=(.5,-.13),ncol=3,frameon=False)
    fig.text(.07,.015,"Fonte: SEEG 10, GWP-AR5. Valores ao lado das UFs são totais absolutos; sem alocação excluído.",fontsize=9)
    fig.tight_layout(rect=(0,.13,1,1))
    return fig
