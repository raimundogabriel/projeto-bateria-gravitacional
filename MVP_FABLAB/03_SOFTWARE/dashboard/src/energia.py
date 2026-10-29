"""
Energia por ciclo e economia simulada.

Segue `03_SOFTWARE/contrato_dados.md`: a economia é **simulada** e vale
energia gerada × tarifa na descida − energia consumida × tarifa na subida.
O consumo da eletrônica fica à parte, fora do rendimento do ramo de potência.
"""
import pandas as pd

J_POR_KWH = 3.6e6
E_TEORICA_J = 2 * 9.81 * 1.70   # 2 kg, 1,70 m (C-101)


def _incrementos(df):
    """Energia de cada intervalo entre leituras (J), a partir dos contadores acumulados."""
    inc = df[["e_subida_j", "e_gerada_j", "e_leds_j", "e_aux_j"]].diff().fillna(0).clip(lower=0)
    inc["custo_rs"] = inc["e_subida_j"] / J_POR_KWH * df["tarifa_rs_kwh"]
    inc["valor_rs"] = inc["e_gerada_j"] / J_POR_KWH * df["tarifa_rs_kwh"]
    return inc


def resumo_energia(df):
    """Totais da janela: energias, rendimento do ramo de potência e economia simulada."""
    inc = _incrementos(df)
    e_sub, e_gen, e_leds, e_aux = (inc[c].sum() for c in ("e_subida_j", "e_gerada_j", "e_leds_j", "e_aux_j"))
    return {
        "ciclos": int(df["ciclo"].iloc[-1] - df["ciclo"].iloc[0]),
        "e_subida_j": e_sub,
        "e_gerada_j": e_gen,
        "e_leds_j": e_leds,
        "e_aux_j": e_aux,
        "rendimento": e_gen / e_sub if e_sub > 0 else None,
        "economia_rs": inc["valor_rs"].sum() - inc["custo_rs"].sum(),
        "custo_aux_rs": (inc["e_aux_j"] / J_POR_KWH * df["tarifa_rs_kwh"]).sum(),
    }


def tabela_ciclos(df):
    """
    Uma linha por descida, com a energia de subida consumida desde a descida
    anterior. O contador `ciclo` do firmware avança ao fim de cada descida.
    """
    inc = _incrementos(df)
    inc["ciclo"] = df["ciclo"].shift(fill_value=df["ciclo"].iloc[0])
    inc["timestamp"] = df["timestamp"]
    inc["tarifa_x_sub"] = inc["e_subida_j"] * df["tarifa_rs_kwh"]
    inc["tarifa_x_gen"] = inc["e_gerada_j"] * df["tarifa_rs_kwh"]

    g = inc.groupby("ciclo")
    ciclos = pd.DataFrame({
        "fim": g["timestamp"].max(),
        "e_subida_j": g["e_subida_j"].sum(),
        "e_gerada_j": g["e_gerada_j"].sum(),
        "e_leds_j": g["e_leds_j"].sum(),
        "tarifa_subida": g["tarifa_x_sub"].sum() / g["e_subida_j"].sum(),
        "tarifa_descida": g["tarifa_x_gen"].sum() / g["e_gerada_j"].sum(),
        "economia_rs": g["valor_rs"].sum() - g["custo_rs"].sum(),
    })
    ciclos = ciclos[ciclos["e_gerada_j"] > 0]
    ciclos["rendimento"] = ciclos["e_gerada_j"] / ciclos["e_subida_j"].where(ciclos["e_subida_j"] > 0)
    return ciclos.reset_index(drop=True).rename_axis("ciclo").reset_index().assign(ciclo=lambda d: d["ciclo"] + 1)


def em_wh(joules):
    return joules / 3600
