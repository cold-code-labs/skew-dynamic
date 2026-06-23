"""Exporta um JSON compacto com todos os resultados para o site (site/src/data/
findings.json). Roda localmente (precisa do dataset); o JSON gerado é versionado
para o build do site não depender do dado bruto.
"""
import json, numpy as np, pandas as pd
from pathlib import Path
from scipy.stats import skew
from skewlib import (io, returns, exante, elo, panel, balance, model, decompose,
                     collapse, premium, cpt, stats, skewmeter as sm, portfolio as port,
                     config as C)

# nomes amigáveis das ligas p/ o widget (fallback = o código football-data)
LEAGUE_NAMES = {
    "E0": "England Premier League", "E1": "England Championship",
    "E2": "England League One", "E3": "England League Two",
    "SC0": "Scotland Premiership", "SC1": "Scotland Championship",
    "SC2": "Scotland League One", "SC3": "Scotland League Two",
    "D1": "Germany Bundesliga", "D2": "Germany 2. Bundesliga",
    "I1": "Italy Serie A", "I2": "Italy Serie B",
    "SP1": "Spain La Liga", "SP2": "Spain Segunda",
    "F1": "France Ligue 1", "F2": "France Ligue 2",
    "N1": "Netherlands Eredivisie", "B1": "Belgium Pro League",
    "P1": "Portugal Primeira", "T1": "Turkey Süper Lig", "G1": "Greece Super League",
    "ARG": "Argentina Primera", "BRA": "Brazil Série A", "MEX": "Mexico Liga MX",
    "USA": "USA MLS", "JAP": "Japan J1", "CHN": "China Super League",
    "RUS": "Russia Premier", "AUT": "Austria Bundesliga", "SWZ": "Switzerland Super",
    "DNK": "Denmark Superliga", "POL": "Poland Ekstraklasa", "IRL": "Ireland Premier",
    "ROU": "Romania Liga I", "NOR": "Norway Eliteserien", "SWE": "Sweden Allsvenskan",
    "FIN": "Finland Veikkausliiga", "BRA2": "Brazil Série B",
}

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
    # skew-meter: lei + se/residual por liga (p/ o widget SkewMeter)
    law = sm.fit_law(df)
    se_by, res_by = {}, {}
    for code, g in df.groupby("Division"):
        if len(g) < 2000:
            continue
        se_by[code] = sm.skew_se(g.p_fav_dv.values, g.o_fav.values)
        res_by[code] = sm.measure(g.p_fav_dv.values, g.o_fav.values)["skew"] \
            - sm.predict_skew(float(g.p_fav_dv.mean()), law)
    leagues = [{"code": r.Division, "name": LEAGUE_NAMES.get(r.Division, r.Division),
                "n": int(r.n), "skew": r.skew_exante, "p_fav": r.p_fav_dv_mean,
                "upset": r.upset_rate, "noll_scully": r.noll_scully,
                "se": se_by.get(r.Division), "residual": res_by.get(r.Division)}
               for r in L.itertuples()]

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

    # E1 — forma fechada de S(σ_L) (quadratura do integral gaussiano)
    from scipy.stats import norm as _norm
    cf = model.smallsigma_coeffs(par["h"], par["c"])
    p0_an = float(_norm.cdf(par["h"] - par["c"]))
    sig_e = np.linspace(0.03, 1.30, 44)
    pf_ex, sk_ex = model.curve_exact(par["h"], par["c"], sig_e)
    sk_mc_e = np.array([model.league_skew(s, par["h"], par["c"], n=300000, seed=7)
                        for s in sig_e])
    sg = np.linspace(0.02, 1.30, 300)
    sk_fine = np.array([model.league_skew_exact(s, par["h"], par["c"]) for s in sg])
    i_pk = int(sk_fine.argmax())
    oe = np.argsort(pf_ex)
    pred_e = np.interp(lg.p_fav_dv_mean.values, pf_ex[oe], sk_ex[oe])
    closed_form = {
        "p0": p0_an, "S0": cf["S0"], "S2": cf["S2"],
        "max_mc_err": float(np.max(np.abs(sk_mc_e - sk_ex))),
        "sigma_peak": float(sg[i_pk]), "skew_peak": float(sk_fine[i_pk]),
        "pfav_peak": float(model.mean_pfav_exact(sg[i_pk], par["h"], par["c"])),
        "league_r": float(np.corrcoef(pred_e, lg.skew_exante.values)[0, 1]),
        "curve": [{"sigma": float(s), "p_fav": float(a), "skew": float(b)}
                  for s, a, b in zip(sig_e, pf_ex, sk_ex)],
    }

    # E2 — robustez da distribuição de força
    from scipy.stats import kurtosis as _kurt
    fams = [("normal", {}, "normal"), ("t", {"nu": 3.0}, "t3"),
            ("t", {"nu": 5.0}, "t5"), ("skewnormal", {"alpha": 4.0}, "skewnormal"),
            ("uniform", {}, "uniform")]
    fcurves = {key: model.curve_family(par["h"], par["c"], sig_e, family=fam,
                                       n=250000, seed=11, **kw)
               for fam, kw, key in fams}
    blo = max(v[0].min() for v in fcurves.values())
    bhi = min(v[0].max() for v in fcurves.values())
    pgr = np.linspace(blo + 0.005, bhi - 0.005, 40)
    nbpf, nbsk = fcurves["normal"]
    base_i = np.interp(pgr, np.sort(nbpf), nbsk[np.argsort(nbpf)])
    force_rob = {"families": []}
    for fam, kw, key in fams:
        pf, sk = fcurves[key]
        si = np.interp(pgr, np.sort(pf), sk[np.argsort(pf)])
        d = model.force_diff(par["sigma_ref"], 300000, 5, fam, **kw)
        force_rob["families"].append({
            "key": key, "exkurt_d": float(_kurt(d)),
            "max_dS": float(np.max(np.abs(si - base_i)))})
    force_rob["max_dS_overall"] = float(max(f["max_dS"] for f in force_rob["families"]))
    force_rob["sd_between_leagues"] = float(lg.skew_exante.std())

    # skew-meter — similaridade de assimetrias (Fase Q) p/ o widget SkewMeter
    import itertools
    skv = np.array([d["skew"] for d in leagues])
    rsv = np.array([d["residual"] for d in leagues if d["residual"] is not None])
    sev = np.array([d["se"] for d in leagues if d["se"] is not None])
    ladder = sm.sufficiency_ladder(df, law)
    big5 = ["E0", "SP1", "I1", "D1", "F1"]; rng = np.random.default_rng(0)
    Ks = [50, 100, 200, 400, 800]; conv_se = []
    for K in Ks:
        errs = []
        for code in big5:
            g = df[df.Division == code]; p = g.p_fav_dv.values; o = g.o_fav.values; n = len(p)
            est = [exante.pooled_skew(p[i], o[i])["skew"]
                   for i in (rng.integers(0, n, K) for _ in range(80))]
            errs.append(float(np.std(est)))
        conv_se.append(float(np.mean(errs)))
    sdb = float(skv.std())
    # métrica de FORMA de Mahalanobis (skew+exkurt): cov amostral de uma liga de
    # referência (E0), invertida — o MESMO objeto auditado no bloco 45 (corr 0.74
    # com |Δskew|). Exportada p/ o widget computar a distância de forma client-side.
    cov_inv = np.linalg.inv(sm.sampling_shape_cov(df[df.Division == "E0"]))
    skewmeter = {
        "median_raw": float(np.median([abs(a - b) for a, b in itertools.combinations(skv, 2)])),
        "median_residual": float(np.median([abs(a - b) for a, b in itertools.combinations(rsv, 2)])),
        "noise_floor": float(np.median(sev)), "sd_between": sdb, "margin": 0.5 * sdb,
        "r2_1param": ladder["r2_1param"], "r2_2moment": ladder["r2_2moment"],
        "r2_full": ladder["r2_full"], "corr_cheap": 0.997, "corr_oddsfree": 0.826,
        "shape_cov_inv": [[float(cov_inv[0, 0]), float(cov_inv[0, 1])],
                          [float(cov_inv[1, 0]), float(cov_inv[1, 1])]],
        "curve": [{"p_fav": float(a), "skew": float(b)}
                  for a, b in zip(law["cpf"], law["csk"])],
    }
    convergence = {"k": Ks, "se": conv_se, "sd_between": sdb}

    # bet-type (bloco 46) — skew ex-ante dos três objetos por liga + global + corr
    btdf = exante.bettype_by(df, min_n=2000).sort_values("p_fav_mean")
    selg = exante.fav_dog_draw(df)
    bettype = {
        "global": {k: exante.pooled_skew(p, o)["skew"] for k, (p, o) in selg.items()},
        "corr": {k: float(np.corrcoef(btdf[f"skew_{k}"].values, btdf.p_fav_mean.values)[0, 1])
                 for k in ("fav", "draw", "dog")},
        "leagues": [{"code": r.Division, "p_fav": r.p_fav_mean, "fav": r.skew_fav,
                     "draw": r.skew_draw, "dog": r.skew_dog} for r in btdf.itertuples()],
    }

    # diversification (bloco 37) — skew do retorno médio de N apostas (≈ skew/√N)
    SIZES = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 509, 800]
    base_f, rows_f = port.skew_decay(df.ret_fav.values, SIZES)
    base_d, rows_d = port.skew_decay(df.ret_dog.values, SIZES)
    diversification = {
        "sizes": SIZES, "base_fav": base_f, "base_dog": base_d,
        "n_gauss_fav": port.n_to_gaussian(base_f), "n_gauss_dog": port.n_to_gaussian(base_d),
        "fav": [round(r["skew"], 4) for r in rows_f],
        "dog": [round(r["skew"], 4) for r in rows_d],
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
        "closed_form": closed_form, "force_robustness": force_rob,
        "skewmeter": skewmeter, "convergence": convergence,
        "bettype": bettype, "diversification": diversification,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(round_rec(data), ensure_ascii=False, indent=0))
    print(f"-> {OUT}  ({OUT.stat().st_size/1024:.1f} KB) | {len(leagues)} ligas, "
          f"{len(panel_rows)} pontos de painel")


if __name__ == "__main__":
    main()
