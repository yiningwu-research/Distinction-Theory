"""
FDS-G1 Companion D demo code: likelihood and falsification interfaces.

This script builds a transparent compressed-data demonstration for finite
screen-capacity residuals. It is intentionally not a final survey likelihood.
Replace the demo CSV files with real Pantheon+/DESI/growth/local-G data vectors
and covariance matrices for production inference.
"""
import json
import os
from dataclasses import dataclass
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FIG = os.path.join(OUT, 'figures')
DAT = os.path.join(OUT, 'data')
os.makedirs(FIG, exist_ok=True)
os.makedirs(DAT, exist_ok=True)

C_OVER_H0_OVER_RD = 29.0  # dimensionless demo scale; not a calibrated rd prior
SIGMA8_0 = 0.80


def E_lcdm(z, Om=0.3):
    z = np.asarray(z)
    return np.sqrt(Om * (1 + z) ** 3 + (1 - Om))


def E_cpl(z, Om=0.3, w0=-1.0, wa=0.0):
    z = np.asarray(z)
    a = 1.0 / (1.0 + z)
    de = (1 - Om) * a ** (-3 * (1 + w0 + wa)) * np.exp(-3 * wa * (1 - a))
    return np.sqrt(Om * a ** (-3) + de)


def chi_g1(a, Om=0.3, s=3.0, chi_inf=1.0):
    chi0 = max(1e-6, 1 - Om)
    B = chi_inf / chi0 - 1.0
    return chi_inf / (1.0 + B * a ** (-s))


def E_g1de(z, Om=0.3, s=3.0, chi_inf=1.0):
    z = np.asarray(z)
    a = 1.0 / (1.0 + z)
    chi = chi_g1(a, Om=Om, s=s, chi_inf=chi_inf)
    denom = np.clip(1.0 - chi, 1e-6, None)
    return np.sqrt(Om * a ** (-3) / denom)


def X_g1(a, Om=0.3, s=3.0, chi_inf=1.0):
    chi = chi_g1(a, Om=Om, s=s, chi_inf=chi_inf)
    return chi * (1.0 - chi / chi_inf)


def comoving_distance(z, Efunc, pars):
    z = np.asarray(z)
    vals = []
    for zz in z:
        grid = np.linspace(0, zz, 160)
        vals.append(np.trapezoid(1.0 / Efunc(grid, **pars), grid))
    return np.array(vals)


def mu_distance(z, Efunc, pars):
    dc = comoving_distance(z, Efunc, pars)
    dl = np.maximum((1 + np.asarray(z)) * dc, 1e-8)
    # Nuisance-free relative distance modulus, anchored by arbitrary offset.
    return 5 * np.log10(dl) + 43.20


def dm_over_rd(z, Efunc, pars):
    return C_OVER_H0_OVER_RD * comoving_distance(z, Efunc, pars)


def dh_over_rd(z, Efunc, pars):
    return C_OVER_H0_OVER_RD / Efunc(z, **pars)


def omega_m_z(z, Om, E):
    return Om * (1 + np.asarray(z)) ** 3 / (E ** 2)


def growth_fs8(z, Efunc, pars, mu0=0.0, sigma8=SIGMA8_0):
    # Lightweight growth-index proxy. Production inference should solve full perturbation equations.
    z = np.asarray(z)
    # Integrate f=d ln D/d ln a from a=1 to a.
    out = []
    Om = pars.get('Om', 0.3)
    s = pars.get('s', 3.0)
    model_is_g1 = Efunc == E_g1de
    for zz in z:
        a = 1.0 / (1.0 + zz)
        aa = np.linspace(1.0, a, 120)
        zz_grid = 1.0 / aa - 1.0
        Eg = Efunc(zz_grid, **pars)
        Omz = omega_m_z(zz_grid, Om, Eg)
        if model_is_g1:
            mu_eff = 1.0 + mu0 * X_g1(aa, Om=Om, s=s, chi_inf=pars.get('chi_inf', 1.0))
        else:
            mu_eff = np.ones_like(aa)
        f = Omz ** 0.55 * (1.0 + 0.5 * (mu_eff - 1.0))
        lnD = np.trapezoid(f, np.log(aa))
        D = np.exp(lnD)
        out.append(f[-1] * sigma8 * D)
    return np.array(out)


def make_demo_data(seed=7):
    rng = np.random.default_rng(seed)
    fid = {'Om': 0.30}
    # SN relative distances
    z_sn = np.array([0.02,0.05,0.10,0.18,0.28,0.40,0.55,0.72,0.90,1.10,1.35])
    mu = mu_distance(z_sn, E_lcdm, fid)
    sig_mu = np.array([0.12,0.10,0.09,0.08,0.08,0.09,0.10,0.11,0.13,0.15,0.18])
    mu_obs = mu + rng.normal(0, sig_mu * 0.35)
    pd.DataFrame({'z':z_sn,'mu':mu_obs,'sigma_mu':sig_mu}).to_csv(os.path.join(DAT,'demo_sn.csv'),index=False)

    # BAO compressed distances
    z_bao = np.array([0.30,0.51,0.70,0.93,1.32,1.80,2.33])
    dm = dm_over_rd(z_bao, E_lcdm, fid)
    dh = dh_over_rd(z_bao, E_lcdm, fid)
    sig_dm = 0.025 * dm
    sig_dh = 0.035 * dh
    dm_obs = dm + rng.normal(0, sig_dm * 0.35)
    dh_obs = dh + rng.normal(0, sig_dh * 0.35)
    pd.DataFrame({'z':z_bao,'DM_over_rd':dm_obs,'sigma_DM':sig_dm,'DH_over_rd':dh_obs,'sigma_DH':sig_dh}).to_csv(os.path.join(DAT,'demo_bao.csv'),index=False)

    # Growth compressed points
    z_g = np.array([0.10,0.25,0.38,0.51,0.70,0.85,1.10])
    fs8 = growth_fs8(z_g, E_lcdm, fid)
    sig_fs8 = np.array([0.045,0.040,0.040,0.045,0.050,0.060,0.070])
    fs8_obs = fs8 + rng.normal(0, sig_fs8 * 0.35)
    pd.DataFrame({'z':z_g,'fsigma8':fs8_obs,'sigma_fs8':sig_fs8}).to_csv(os.path.join(DAT,'demo_growth.csv'),index=False)


def load_demo_data():
    return {
        'sn': pd.read_csv(os.path.join(DAT,'demo_sn.csv')),
        'bao': pd.read_csv(os.path.join(DAT,'demo_bao.csv')),
        'growth': pd.read_csv(os.path.join(DAT,'demo_growth.csv')),
    }


def chi2_model(kind, pars, data):
    if kind == 'lcdm':
        Efunc = E_lcdm
        ep = {'Om': pars['Om']}
        mu0 = 0.0
    elif kind == 'cpl':
        Efunc = E_cpl
        ep = {'Om': pars['Om'], 'w0': pars['w0'], 'wa': pars['wa']}
        mu0 = 0.0
    elif kind in ('g1de','g1de_mu'):
        Efunc = E_g1de
        ep = {'Om': pars['Om'], 's': pars['s']}
        mu0 = pars.get('mu0', 0.0)
    else:
        raise ValueError(kind)

    sn = data['sn']
    mu_pred = mu_distance(sn.z.values, Efunc, ep)
    # marginalize a constant SN offset analytically by fitting weighted offset
    delta = sn.mu.values - mu_pred
    w = 1.0 / sn.sigma_mu.values**2
    offset = np.sum(w*delta)/np.sum(w)
    c2_sn = np.sum(((delta-offset)/sn.sigma_mu.values)**2)

    bao = data['bao']
    dm_pred = dm_over_rd(bao.z.values, Efunc, ep)
    dh_pred = dh_over_rd(bao.z.values, Efunc, ep)
    c2_bao = np.sum(((bao.DM_over_rd.values-dm_pred)/bao.sigma_DM.values)**2) + np.sum(((bao.DH_over_rd.values-dh_pred)/bao.sigma_DH.values)**2)

    gr = data['growth']
    fs_pred = growth_fs8(gr.z.values, Efunc, ep, mu0=mu0)
    c2_g = np.sum(((gr.fsigma8.values-fs_pred)/gr.sigma_fs8.values)**2)

    # Local priors: no free G drift and weak growth residual. Demo values only.
    c2_local = 0.0
    if kind in ('g1de','g1de_mu'):
        # In this demo, s=3 is LCDM-like. Penalize large departure as a no-free-drift proxy.
        c2_local += ((pars['s']-3.0)/0.50)**2
    if kind == 'g1de_mu':
        c2_local += (pars.get('mu0',0.0)/0.20)**2
    return float(c2_sn + c2_bao + c2_g + c2_local)


def scan_models():
    data = load_demo_data()
    results = []
    # LCDM one parameter
    best = (1e9,None)
    for Om in np.linspace(0.24,0.38,31):
        c2 = chi2_model('lcdm', {'Om':Om}, data)
        if c2 < best[0]: best=(c2,{'Om':Om})
    results.append(('LCDM', 'lcdm', best[0], best[1], 1))

    # CPL coarse scan
    best = (1e9,None)
    for Om in np.linspace(0.26,0.36,11):
      for w0 in np.linspace(-1.25,-0.75,11):
        for wa in np.linspace(-0.8,0.8,9):
            c2 = chi2_model('cpl', {'Om':Om,'w0':w0,'wa':wa}, data)
            if c2 < best[0]: best=(c2,{'Om':Om,'w0':w0,'wa':wa})
    results.append(('CPL', 'cpl', best[0], best[1], 3))

    # G1DE background
    best = (1e9,None)
    grid_rows=[]
    for Om in np.linspace(0.24,0.38,31):
      for s in np.linspace(2.2,3.8,81):
        c2 = chi2_model('g1de', {'Om':Om,'s':s}, data)
        grid_rows.append({'Om':Om,'s':s,'chi2':c2})
        if c2 < best[0]: best=(c2,{'Om':Om,'s':s})
    pd.DataFrame(grid_rows).to_csv(os.path.join(DAT,'g1de_grid.csv'),index=False)
    results.append(('G1DE', 'g1de', best[0], best[1], 2))

    # G1DE + growth residual
    best = (1e9,None)
    for Om in np.linspace(0.26,0.34,17):
      for s in np.linspace(2.5,3.5,21):
        for mu0 in np.linspace(-0.30,0.30,11):
          c2 = chi2_model('g1de_mu', {'Om':Om,'s':s,'mu0':mu0}, data)
          if c2 < best[0]: best=(c2,{'Om':Om,'s':s,'mu0':mu0})
    results.append(('G1DE+mu', 'g1de_mu', best[0], best[1], 3))

    n = len(data['sn']) + 2*len(data['bao']) + len(data['growth']) + 2
    rows=[]
    for label, kind, chi2, pars, k in results:
        rows.append({'model':label, 'chi2':chi2, 'k':k, 'n':n, 'AIC':chi2+2*k, 'BIC':chi2+k*np.log(n), 'best_parameters':json.dumps(pars)})
    df = pd.DataFrame(rows)
    df['Delta_AIC'] = df.AIC - df.AIC.min()
    df['Delta_BIC'] = df.BIC - df.BIC.min()
    df.to_csv(os.path.join(DAT,'model_comparison.csv'),index=False)
    return df


def make_figures(df):
    # Figure 1: model comparison
    labels = df['model'].values
    x = np.arange(len(labels))
    plt.figure(figsize=(7,4))
    plt.bar(x, df['Delta_AIC'].values, alpha=0.75, label='Delta AIC')
    plt.plot(x, df['Delta_BIC'].values, marker='o', label='Delta BIC')
    plt.xticks(x, labels, rotation=20)
    plt.ylabel('Information criterion difference')
    plt.title('Demo compressed-data model comparison')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIG,'model_comparison_aic_bic.png'), dpi=200)
    plt.close()

    # Figure 2: G1DE grid likelihood in Om-s
    grid = pd.read_csv(os.path.join(DAT,'g1de_grid.csv'))
    pivot = grid.pivot(index='s', columns='Om', values='chi2')
    plt.figure(figsize=(6,4.5))
    plt.contourf(pivot.columns.values, pivot.index.values, pivot.values - np.nanmin(pivot.values), levels=20)
    plt.colorbar(label='Delta chi2')
    plt.xlabel(r'$\Omega_{m0}$')
    plt.ylabel('s')
    plt.title('G1DE compressed-likelihood surface')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG,'g1de_grid_delta_chi2.png'), dpi=200)
    plt.close()

    # Figure 3: signatures relative to LCDM
    z = np.linspace(0.0,2.0,200)
    Om=0.30
    curves = []
    for s in [2.7,3.0,3.3]:
        Eg = E_g1de(z, Om=Om, s=s)
        El = E_lcdm(z, Om=Om)
        curves.append((s, Eg/El - 1))
    plt.figure(figsize=(6,4))
    for s, y in curves:
        plt.plot(z, y, label=f's={s:.1f}')
    plt.axhline(0, linewidth=0.8)
    plt.xlabel('z')
    plt.ylabel(r'$E_{G1DE}/E_{LCDM}-1$')
    plt.title('Background residual signature')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIG,'background_residual_signatures.png'), dpi=200)
    plt.close()

    # Figure 4: finite-area suppression
    A = np.logspace(0,8,300)
    for alpha in [-1.0,1.0,5.0]:
        dG = -alpha/(A + alpha) # eta0=1 toy exactly from eta_delta=1+alpha/A
        plt.loglog(A, np.abs(dG), label=f'|alpha|={abs(alpha):.0f}')
    plt.xlabel(r'$A/a_0$')
    plt.ylabel(r'$|\Delta G/G|$')
    plt.title('Finite-area response suppression')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIG,'finite_area_suppression.png'), dpi=200)
    plt.close()

    # Figure 5: falsification flow chart as simple text figure
    fig, ax = plt.subplots(figsize=(8,4.5))
    ax.axis('off')
    steps = [
        'Define screen-response model',
        'Check conservation closure',
        'Compute H(z), growth, lensing, local G',
        'Run compressed likelihood',
        'Compare with LCDM/CPL/scalar-tensor',
        'Pass / fail / refine residual class'
    ]
    y = 0.9
    for i, step in enumerate(steps):
        ax.text(0.5, y, step, ha='center', va='center', bbox=dict(boxstyle='round', fc='white', ec='black'))
        if i < len(steps)-1:
            ax.annotate('', xy=(0.5,y-0.09), xytext=(0.5,y-0.03), arrowprops=dict(arrowstyle='->'))
        y -= 0.15
    plt.tight_layout()
    plt.savefig(os.path.join(FIG,'falsification_pipeline.png'), dpi=200)
    plt.close()


def make_tables():
    # Observable dictionary
    obs = pd.DataFrame([
        {'observable':'SN distance modulus mu(z)', 'tests':'background expansion', 'G1 quantity':'chi_H(a) or E(a)', 'failure mode':'cannot match distances without excessive parameters'},
        {'observable':'BAO DM/rd, DH/rd, DV/rd', 'tests':'expansion geometry', 'G1 quantity':'E(a), comoving distance', 'failure mode':'background residual inconsistent with BAO'},
        {'observable':'f sigma8(z)', 'tests':'growth of structure', 'G1 quantity':'mu(a), chi_H(a)', 'failure mode':'growth-lensing correlation fails'},
        {'observable':'lensing proxy Sigma(a)', 'tests':'Weyl response', 'G1 quantity':'Sigma0 X(a)', 'failure mode':'lensing residual independent of ledger shape'},
        {'observable':'dotG/G', 'tests':'capacity drift', 'G1 quantity':'alpha_M=-dotG/(HG)', 'failure mode':'free macroscopic G drift'},
        {'observable':'GW speed flag', 'tests':'tensor propagation', 'G1 quantity':'alpha_T', 'failure mode':'non-luminal tensor sector'},
    ])
    obs.to_csv(os.path.join(DAT,'observable_dictionary.csv'), index=False)
    crit = pd.DataFrame([
        {'criterion':'No free macroscopic G drift', 'pass condition':'|dotG/G| below local/cosmological bounds or screened/closed by residual sector', 'fail condition':'unscreened eta drift required by fit'},
        {'criterion':'Correlated residuals', 'pass condition':'same ledger variable explains expansion-growth-lensing pattern', 'fail condition':'independent arbitrary functions needed'},
        {'criterion':'Finite-area suppression', 'pass condition':'ordinary area corrections suppressed as 1/A for large screens', 'fail condition':'large macroscopic corrections from log terms alone'},
        {'criterion':'Information penalty', 'pass condition':'competitive AIC/BIC/Bayes factor against simple baselines', 'fail condition':'improvement disappears after parameter penalty'},
    ])
    crit.to_csv(os.path.join(DAT,'falsification_criteria.csv'), index=False)


def main():
    make_demo_data()
    make_tables()
    df = scan_models()
    make_figures(df)
    print(df)
    print('Wrote outputs to', OUT)

if __name__ == '__main__':
    main()
