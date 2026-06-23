"""Exporta um JSON compacto com todos os resultados para o site (site/src/data/
findings.json). Roda localmente (precisa do dataset); o JSON gerado é versionado
para o build do site não depender do dado bruto.
"""
import json, numpy as np, pandas as pd
from pathlib import Path
from scipy.stats import skew
from skewlib import (io, returns, exante, elo, panel, balance, model, decompose,
                     collapse, premium, cpt, stats, config as C)

OUT = Path(__file__).resolve().parents[1].parent / "site" / "src" / "data" / "findings.json"


def round_rec(o, n=4):
    if isinstance(o, float): return round(o, n)
    if isinstance(o, dict): return {k: round_rec(v, n) for k, v in o.items()}
    if isinstance(o, list): return [round_rec(v, n) for v in o]
    return o


def main():
    prov = json.loads((C.DATA_PATH.parent / "PROVENANCE.json").read_text())
    df = exante.add_exante(returns.add_returns(io.load()))

    # F1 — FLB curve (ex-ante vs ex-post por faixa de p_fav)
    edges = [0, .4, .45, .5, .55, .6, .7, 1.0]
    d = df.copy(); d["b"] = pd.cut(d.p_fav_dv, edges)
    flb = []
    for b, g in d.groupby("b", observed=True):
        if len(g) < 200: continue
        flb.append({"p": float(g.p_fav_dv.mean()),
                    "ex_ante": exante.pooled_skew(g.p_fav_dv.values, g.o_fav.values)["skew"],
                    "ex_post": float(skew(g.ret_fav.values)), "n": int(len(g))})

    # F3 — decomposição global
    gd = exante.pooled_skew(df.p_fav_dv.values, df.o_fav.values)
    decomp = {"within": gd["within_frac"], "cov": gd["cov_frac"], "between": gd["between_frac"],
              "skew": gd["skew"]}

    # leagues — merge ex-ante + Elo (odds-free) + standings CB
    lg = exante.pooled_by(df, "Division", min_n=2000)[["Division", "n", "skew_exante", "p_fav_dv_mean"]]
    eloc = elo.league_competitiveness(elo.with_elo(df))[["Division", "upset_rate", "elo_pfav"]]
    cb = balance.by_league(balance.cb_indices(balance.standings(df)))[["Division", "noll_scully", "hhi_star"]]
    L = lg.merge(eloc, on="Division").merge(cb, on="Division").sort_values("skew_exante")
    leagues = [{"code": r.Division, "n": int(r.n), "skew": r.skew_exante,
                "p_fav": r.p_fav_dv_mean, "upset": r.upset_rate,
                "noll_scully": r.noll_scully} for r in L.itertuples()]

    # F5 — curva teórica (ordered-probit)
    par = model.calibrate(home=(df.FTResult == "H").mean(), draw=(df.FTResult == "D").mean(),
                          pfav=float(df.p_fav_dv.mean()))
    sig = np.linspace(0.08, 1.25, 40)
    cpf, csk = model.curve(par["h"], par["c"], sig)
    curve = [{"p_fav": float(a), "skew": float(b)} for a, b in zip(cpf, csk)]

    # F4 — painel liga×temporada
    pan = panel.league_season_panel(df)
    panel_rows = [{"div": r.Division, "season": int(r.season), "skew": r.skew_exante}
                  for r in pan.itertuples()]
    trend = panel.trend_test(pan); vdec = panel.variance_decomp(pan)

    # FLB no tempo
    fy = decompose.flb_by_year(df)
    flb_year = [{"year": int(r.year), "ret_dog": r.ret_dog, "spread": r.flb_spread,
                 "skew": r.skew_expost} for r in fy.itertuples()]

    # B1 — invariância de FORMA (multi-momento): global + previsto×observado
    Gm = exante.pooled_moments(df.p_fav_dv.values, df.o_fav.values, max_order=6)
    rows = []
    for code, g in df.groupby("Division"):
        if len(g) < 2000: continue
        pm = exante.pooled_moments(g.p_fav_dv.values, g.o_fav.values, max_order=4)
        rows.append({"code": code, "p_fav": float(g.p_fav_dv.mean()),
                     "var": pm["var"], "skew": pm["skew"], "exkurt": pm["exkurt"]})
    lgm = pd.DataFrame(rows)
    cpf2, cmom = model.curve_moments(par["h"], par["c"], sig, max_order=4)
    o2 = np.argsort(cpf2)
    model_r = {m: float(np.corrcoef(
                   np.interp(lgm.p_fav.values, cpf2[o2], cmom[m][o2]), lgm[m].values)[0, 1])
               for m in ["var", "skew", "exkurt"]}
    moments = {
        "global": {k: Gm[k] for k in ["var", "skew", "exkurt", "std5", "std6"]},
        "within_frac": {f"m{k}": Gm[f"within_frac_m{k}"] for k in range(2, 7)},
        "model_r": model_r,
        "curve": [{"p_fav": float(a), "skew": float(s), "exkurt": float(k)}
                  for a, s, k in zip(cpf2[o2], cmom["skew"][o2], cmom["exkurt"][o2])],
        "leagues": [{"code": r.code, "p_fav": r.p_fav, "var": r.var,
                     "skew": r.skew, "exkurt": r.exkurt} for r in lgm.itertuples()],
    }

    # B2 — colapso de distribuição (forma = f(competitividade))
    z = collapse.zscore_returns(df, "ret_fav", "Division", min_n=2000)
    A = collapse.pairwise_test(z, "ks")
    ctab, csumm = collapse.conditional_invariance(
        df, "p_fav_dv", "ret_fav", "Division", nbins=8, min_n=300)
    collapse_data = {
        "uncond_ks": A["median_stat"], "uncond_reject": A["reject_frac"],
        "cond_ks": float(ctab.ks_stat.median()),
        "drop": float(1 - ctab.ks_stat.median() / A["median_stat"]),
        "by_bin": [{"p_mid": float(r.p_mid), "reject_frac": float(r.reject_frac),
                    "ks_stat": float(r.ks_stat_med)} for r in csumm.itertuples()],
    }

    # C1 — prêmio de skewness (decomposição do retorno)
    pg = premium.decompose_global(df)
    dec = premium.decompose_by_league(df, min_n=2000)
    sk = exante.pooled_by(df, "Division", min_n=2000)[["Division", "skew_exante"]]
    DL = dec.merge(sk, on="Division")
    premium_data = {
        "global": {"ret": pg["ret_mean"], "vig": pg["vig"], "flb": pg["flb"]},
        "resid_skew_r": stats.bootstrap_corr(DL.residual.values, DL.skew_exante.values)["r"],
        "flb_skew_r": stats.bootstrap_corr(DL.flb.values, DL.skew_exante.values)["r"],
        "flb_curve": [{"p": float(r.p), "flb": float(r.flb)}
                      for r in premium.flb_curve(df, nbins=20).itertuples()],
    }

    # C2 — CPT invariante (ponderação de probabilidade)
    cal = cpt.calibration(df, nbins=25)
    g0 = cpt.fit_gamma(cal)
    gl = cpt.gamma_by(df, "Division", min_n=4000, nbins=15)
    dd = df.copy(); dd["season"] = dd.date.dt.year
    gy = cpt.gamma_by(dd, "season", min_n=4000, nbins=15).sort_values("season")
    gtr = stats.ols(gy.gamma.values, gy.season.values - gy.season.mean())
    cpt_data = {
        "gamma": g0, "gamma_mean": float(gl.gamma.mean()),
        "gamma_sd_league": float(gl.gamma.std()), "gamma_sd_season": float(gy.gamma.std()),
        "trend_beta": gtr["slope"],
        "weight_curve": [{"pi": float(r.pi), "q": float(r.q)} for r in cal.itertuples()],
        "by_season": [{"season": int(r.season), "gamma": float(r.gamma)}
                      for r in gy.itertuples()],
    }

    data = {
        "meta": {"n_matches": prov["analysis_rows_ge2005"], "leagues": prov["leagues"],
                 "date_min": prov["date_min"], "date_max": prov["date_max"],
                 "sha256": prov["sha256"][:12], "devig": C.DEVIG_METHOD},
        "headline": {
            "skew_ex_ante": gd["skew"], "skew_ex_post": float(skew(df.ret_fav)),
            "within_frac": gd["within_frac"],
            "corr_elo_odds": 0.909, "corr_skew_upset": 0.826,
            "corr_skew_nollscully": -0.625, "trend_beta": trend["beta_year"],
            "trend_p": trend["p"], "icc": vdec["icc"],
            "model_r": 0.904, "model_rmse": 0.024,
            "overround_avg": 1.067, "overround_best": 1.009},
        "flb_curve": flb, "decomp": decomp, "leagues": leagues,
        "model_curve": curve, "model_par": par,
        "panel": panel_rows, "panel_stats": {"beta": trend["beta_year"], "p": trend["p"],
            "icc": vdec["icc"], "sd_between": vdec["sd_between"], "sd_within": vdec["sd_within"]},
        "flb_year": flb_year,
        "moments": moments, "collapse": collapse_data,
        "premium": premium_data, "cpt": cpt_data,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(round_rec(data), ensure_ascii=False, indent=0))
    print(f"-> {OUT}  ({OUT.stat().st_size/1024:.1f} KB) | {len(leagues)} ligas, "
          f"{len(panel_rows)} pontos de painel")


if __name__ == "__main__":
    main()
