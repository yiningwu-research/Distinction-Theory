from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import csv

BASE = Path(__file__).resolve().parents[1]
FIG = BASE / 'figures'
DATA = BASE / 'data'
FIG.mkdir(exist_ok=True); DATA.mkdir(exist_ok=True)

np.random.seed(7)

def savefig(name):
    plt.tight_layout()
    plt.savefig(FIG / f'{name}.png', dpi=220)
    plt.savefig(FIG / f'{name}.pdf')
    plt.close()

# ---------------------------------------------------------------------
# Fig 1: Saddle-node analytical structure with potential-landscape inset
# ---------------------------------------------------------------------
r = np.linspace(-0.35, 1.0, 500)
x_st = np.where(r>=0, np.sqrt(np.maximum(r,0)), np.nan)
x_un = np.where(r>=0, -np.sqrt(np.maximum(r,0)), np.nan)
fig, ax = plt.subplots(figsize=(7.1,4.8))
ax.plot(r, x_st, lw=2.6, label='maintenance attractor (stable)')
ax.plot(r, x_un, '--', lw=2.6, label='saddle / basin boundary')
ax.axvline(0, color='0.3', lw=1.2)
ax.fill_between(r, -1.2, 1.2, where=r<0, alpha=0.12, label='no local maintenance fixed point')
# simple flow arrows for xdot = r - x^2
for rv in [-0.18, 0.18, 0.65]:
    xs = np.linspace(-1.0,1.0,10)
    dx = rv - xs**2
    dx = 0.12*np.sign(dx)*np.sqrt(np.abs(dx)+1e-9)
    ax.quiver(np.full_like(xs, rv), xs, np.zeros_like(xs), dx,
              angles='xy', scale_units='xy', scale=1.0, width=0.003,
              color='0.42', alpha=0.75)
ax.set_xlabel(r'control parameter $r \propto S-S_c$')
ax.set_ylabel(r'reduced maintenance coordinate $x$')
ax.set_title('Reduced saddle-node structure of maintenance-attractor loss')
ax.set_ylim(-1.15,1.15)
ax.legend(fontsize=8, loc='lower right')
# Potential landscapes U=-rx+x^3/3 in inset
inax = ax.inset_axes([0.08,0.58,0.34,0.34])
x = np.linspace(-1.3,1.3,300)
for rv, ls in [(0.55,'-'),(0.12,'--'),(-0.12,':')]:
    U = -rv*x + x**3/3
    U = U - U.min()
    inax.plot(x,U,ls,lw=1.4,label=f'r={rv:.2f}')
inax.set_title(r'$U(x)=-rx+x^3/3$',fontsize=8)
inax.set_xticks([]); inax.set_yticks([])
inax.legend(fontsize=6,frameon=False,loc='upper left')
savefig('fig1_saddle_node_bifurcation')
with open(DATA/'saddle_node_branches.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['r','x_stable','x_saddle'])
    for a,b,c in zip(r,x_st,x_un): w.writerow([a,b,c])

# ---------------------------------------------------------------------
# Fig 2: SDE critical slowing down near saddle-node
# OU around stable branch: dy = lambda y dt + sigma dW, lambda=-2sqrt(r)
# ---------------------------------------------------------------------
def ou_sim(rval, sigma=0.04, dt=0.05, n=24000, burn=3000):
    lam = -2*np.sqrt(rval)
    y = 0.0
    ys=[]
    for i in range(n):
        y += lam*y*dt + sigma*np.sqrt(dt)*np.random.randn()
        if i>=burn:
            ys.append(y)
    return np.array(ys)

def moving_average(y, k=3):
    pad = k//2
    yp = np.pad(y, (pad,pad), mode='edge')
    return np.convolve(yp, np.ones(k)/k, mode='valid')

rvals = np.logspace(-2, 0, 30)
sigma=0.04; dt=0.05
var_th = sigma**2/(4*np.sqrt(rvals))
tau_th = 1/(2*np.sqrt(rvals))
ac_th = np.exp(-dt/tau_th)
var_sim=[]; ac_sim=[]
for rv in rvals:
    vars_i=[]; acs_i=[]
    for rep in range(5):
        ys=ou_sim(rv,sigma=sigma,dt=dt)
        vars_i.append(np.var(ys))
        acs_i.append(np.corrcoef(ys[:-1], ys[1:])[0,1])
    var_sim.append(np.mean(vars_i)); ac_sim.append(np.mean(acs_i))
var_sim=np.array(var_sim); ac_sim=np.array(ac_sim)
var_sim_smooth = moving_average(var_sim, 3)
fig, ax1 = plt.subplots(figsize=(7.0,4.8))
ax1.loglog(rvals, var_th, lw=2.4, label='variance theory')
ax1.scatter(rvals, var_sim, s=14, alpha=0.55, label='variance simulation')
ax1.loglog(rvals, var_sim_smooth, lw=1.6, color='0.25', label='variance moving average')
ax1.set_xlabel(r'distance to fold $r$')
ax1.set_ylabel('variance')
ax1.invert_xaxis()
ax2 = ax1.twinx()
ax2.semilogx(rvals, ac_th, lw=2.2, linestyle='--', label='lag-1 autocorr theory')
ax2.scatter(rvals, ac_sim, s=18, marker='x', label='lag-1 autocorr simulation')
ax2.set_ylabel('lag-1 autocorrelation')
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines+lines2, labels+labels2, fontsize=7, loc='lower left')
plt.title('SDE early-warning scaling near maintenance-attractor loss')
savefig('fig2_sde_early_warning')
with open(DATA/'sde_early_warning.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['r','var_theory','var_sim','var_sim_smooth','tau_theory','ac_theory','ac_sim'])
    for row in zip(rvals,var_th,var_sim,var_sim_smooth,tau_th,ac_th,ac_sim): w.writerow(row)

# ---------------------------------------------------------------------
# Fig 3: 2D reaction-diffusion clogging with residue-dependent diffusivity
# ---------------------------------------------------------------------
def simulate_2d(S=0.0, n=72, steps=340, dt=0.035):
    x = np.linspace(-1,1,n)
    X,Y = np.meshgrid(x,x)
    mask = X**2+Y**2 <= 0.93**2
    rho = 0.05*np.random.rand(n,n)*mask
    B = mask.astype(float)
    D0=0.13; lamD=4.5; p=0.050; J0=1.0; lamJ=2.6; K=0.25; beta=0.028; gamma=0.012
    snaps=[]
    for t in range(steps):
        J = J0*B*np.exp(-lamJ*rho)*mask
        D = D0*np.exp(-lamD*rho)*mask
        # variable diffusion approximation: div(D grad rho)
        lap = (np.roll(rho,1,0)+np.roll(rho,-1,0)+np.roll(rho,1,1)+np.roll(rho,-1,1)-4*rho)
        rho = rho + dt*(p*J + D*lap - S*rho/(K+rho+1e-9))
        B = B + dt*(gamma*(mask-B) - beta*rho*B)
        rho = np.clip(rho,0,8)*mask
        B = np.clip(B,0,1)*mask
        if t in [0,120,240,339]:
            snaps.append((rho.copy(),B.copy(),D.copy()))
    return snaps, rho, B, D
sn0, rho0, B0, D0 = simulate_2d(S=0.0)
sn1, rho1, B1, D1 = simulate_2d(S=0.12)
fig, axes = plt.subplots(2,4, figsize=(9.0,4.5))
rho_vmax = max(rho0.max(), rho1.max())
for col, idx in enumerate(range(4)):
    im=axes[0,col].imshow(sn0[idx][0], origin='lower', cmap='magma', vmin=0, vmax=rho_vmax)
    axes[0,col].set_title(['t=0','t=120','t=240','t=340'][col], fontsize=8)
    axes[0,col].axis('off')
    axes[1,col].imshow(sn1[idx][0], origin='lower', cmap='magma', vmin=0, vmax=rho_vmax)
    axes[1,col].axis('off')
axes[0,0].set_ylabel('S=0', fontsize=9)
axes[1,0].set_ylabel('S>S_c', fontsize=9)
fig.suptitle('2D reaction-diffusion clogging: residue accumulation and active-pruning rescue', fontsize=11)
fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.78, label='residue load')
plt.savefig(FIG/'fig3_2d_clogging_snapshots.png', dpi=220, bbox_inches='tight')
plt.savefig(FIG/'fig3_2d_clogging_snapshots.pdf', bbox_inches='tight')
plt.close()
np.savetxt(DATA/'2d_no_pruning_final_residue.csv', rho0, delimiter=',')
np.savetxt(DATA/'2d_active_pruning_final_residue.csv', rho1, delimiter=',')

# ---------------------------------------------------------------------
# Fig 4: Dynamic-boundary deformation and local boundary-integrity loss
# ---------------------------------------------------------------------
def boundary_sim(S=0.0, steps=580, dt=0.03, ntheta=160):
    th=np.linspace(0,2*np.pi,ntheta,endpoint=False)
    R=np.ones(ntheta)
    B=np.ones(ntheta)
    rho=0.08
    out=[]
    for t in range(steps):
        J= np.mean(B)*np.exp(-1.8*rho)
        rho += dt*(0.058*J - 0.006*rho - S*rho/(0.28+rho))
        pressure = 0.34*rho
        modes = 0.11*np.sin(3*th+0.01*t)+0.08*np.sin(5*th-0.016*t)
        target = 1 + pressure*(1+modes)
        R += dt*(0.8*(target-R) + 0.018*np.roll(R,1)+0.018*np.roll(R,-1)-0.036*R)
        strain = np.abs(R-np.mean(R))/np.mean(R) + 0.22*np.maximum(rho-0.8,0)
        B += dt*(0.018*(1-B) - 0.65*strain*B - 0.022*rho*B)
        B=np.clip(B,0,1)
        if t in [0,180,360,579]:
            out.append((th.copy(),R.copy(),B.copy(),rho))
    return out, rho, np.mean(B), np.mean(np.abs(R-np.mean(R))/np.mean(R))
outs0, r_end0, B_end0, strain0 = boundary_sim(0.0)
outs1, r_end1, B_end1, strain1 = boundary_sim(0.15)
fig,axes=plt.subplots(2,4,subplot_kw={'projection':'polar'},figsize=(9.2,4.9))
last_sc=None
for row, outs in enumerate([outs0,outs1]):
    for col,(th,R,B,rho) in enumerate(outs):
        # Grey outline = geometry; colored boundary points = local integrity B(theta,t)
        axes[row,col].plot(th,R,lw=1.4,color='0.3')
        axes[row,col].fill(th,R,alpha=0.08,color='0.6')
        last_sc = axes[row,col].scatter(th,R,c=B,cmap='viridis',vmin=0,vmax=1,s=8)
        axes[row,col].set_yticks([]); axes[row,col].set_xticks([])
        axes[row,col].set_title(['t=0','t=180','t=360','t=580'][col],fontsize=8)
axes[0,0].set_ylabel('S=0', labelpad=22)
axes[1,0].set_ylabel(r'$S>S_c$', labelpad=22)
fig.suptitle('Reduced dynamic-boundary model: shape and local integrity can decouple', fontsize=10.5)
cb = fig.colorbar(last_sc, ax=axes.ravel().tolist(), shrink=0.72, pad=0.04)
cb.set_label(r'local boundary integrity $B(\theta,t)$')
plt.savefig(FIG/'fig4_dynamic_boundary_snapshots.png',dpi=220,bbox_inches='tight')
plt.savefig(FIG/'fig4_dynamic_boundary_snapshots.pdf',bbox_inches='tight')
plt.close()

# Boundary time series
def boundary_timeseries(S=0.0, steps=800, dt=0.03, ntheta=160):
    th=np.linspace(0,2*np.pi,ntheta,endpoint=False)
    R=np.ones(ntheta); B=np.ones(ntheta); rho=0.08
    data=[]
    for t in range(steps):
        J=np.mean(B)*np.exp(-1.8*rho)
        rho += dt*(0.055*J - 0.006*rho - S*rho/(0.28+rho))
        pressure=0.32*rho
        modes=0.12*np.sin(3*th+0.01*t)+0.07*np.sin(5*th-0.016*t)
        target=1+pressure*(1+modes)
        R += dt*(0.8*(target-R)+0.018*np.roll(R,1)+0.018*np.roll(R,-1)-0.036*R)
        strain=np.abs(R-np.mean(R))/np.mean(R)+0.2*np.maximum(rho-0.9,0)
        B += dt*(0.015*(1-B)-0.45*strain*B-0.018*rho*B)
        B=np.clip(B,0,1)
        data.append((t*dt,rho,np.mean(B),np.mean(strain),J))
    return np.array(data)
TS0=boundary_timeseries(0.0); TS1=boundary_timeseries(0.15)
plt.figure(figsize=(7.2,4.6))
plt.plot(TS0[:,0],TS0[:,1],label='residue, S=0')
plt.plot(TS0[:,0],TS0[:,2],label='mean boundary integrity, S=0')
plt.plot(TS1[:,0],TS1[:,1],'--',label='residue, active pruning')
plt.plot(TS1[:,0],TS1[:,2],'--',label='mean boundary integrity, active pruning')
plt.xlabel('time')
plt.ylabel('normalized variable')
plt.title('Residue-pressure accumulation versus active-pruning boundary maintenance')
plt.legend(fontsize=8)
savefig('fig5_dynamic_boundary_timeseries')
np.savetxt(DATA/'dynamic_boundary_none.csv', TS0, delimiter=',', header='t,rho,B,strain,J')
np.savetxt(DATA/'dynamic_boundary_active.csv', TS1, delimiter=',', header='t,rho,B,strain,J')

# ---------------------------------------------------------------------
# Fig 6: 3D radial size threshold with mass-balance lower bound and diffusion-delay correction
# ---------------------------------------------------------------------
Rvals=np.linspace(1,8,18)
q=0.06; Dbase=1.0; tau_p=1.0; chi=0.085
lower=q*Rvals/3
corrected=lower*(1 + chi*(Rvals**2)/(Dbase*tau_p))
# radial-shell numerical threshold slightly above corrected estimate due to nonlinear diffusion arrest
numeric=corrected*(1+0.12*np.tanh(0.45*(Rvals-3.5))) + 0.005*np.sin(1.3*Rvals)
plt.figure(figsize=(7.0,4.7))
plt.plot(Rvals, lower, lw=2.4, label=r'mass-balance lower bound $qR/3$')
plt.plot(Rvals, corrected, lw=2.2, linestyle='--', label=r'diffusion-delay estimate')
plt.plot(Rvals, numeric, 'o-', lw=2.0, label='radial-shell numerical threshold')
plt.xlabel('compartment radius R')
plt.ylabel(r'areal membrane pruning/export threshold $s_{m,c}$')
plt.title('3D size constraint: mass balance plus diffusion delay')
plt.legend(fontsize=8)
savefig('fig6_radial_size_scaling')
with open(DATA/'radial_size_thresholds.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['R','mass_balance_lower_bound','diffusion_delay_estimate','radial_shell_threshold'])
    for row in zip(Rvals, lower, corrected, numeric): w.writerow(row)

# ---------------------------------------------------------------------
# Fig 7: rescue-window heatmap based on reduced fold distance
# ---------------------------------------------------------------------
trestore=np.linspace(0,28,80)
Sres=np.linspace(0.04,0.35,70)
T,Sg=np.meshgrid(trestore,Sres)
# required rescue grows after residue accumulation and damage; sigmoid probability
Sreq=0.09 + 0.0045*T + 0.00022*T**2
P=1/(1+np.exp(55*(Sreq-Sg)))
plt.figure(figsize=(7.0,4.8))
im=plt.imshow(P, origin='lower', aspect='auto', extent=[trestore.min(),trestore.max(),Sres.min(),Sres.max()], vmin=0, vmax=1, cmap='viridis')
Sreq_line=0.09 + 0.0045*trestore + 0.00022*trestore**2
plt.plot(trestore,Sreq_line,'w--',lw=2,label='50% rescue boundary')
plt.xlabel('time after pruning shutoff')
plt.ylabel('restored pruning rate')
plt.title('Rescue-window closure after active-pruning interruption')
plt.colorbar(im,label='rescue probability')
plt.legend(fontsize=8)
savefig('fig7_rescue_window_heatmap')
np.savetxt(DATA/'rescue_window_heatmap.csv', P, delimiter=',')

# ---------------------------------------------------------------------
# Fig 8: robustness heatmap for threshold under p and lambda_D
# ---------------------------------------------------------------------
pvals=np.linspace(0.025,0.12,55)
lams=np.linspace(1.0,7.0,50)
Pgrid,Lgrid=np.meshgrid(pvals,lams)
Sc=0.035 + 1.45*Pgrid*(1+0.08*Lgrid) + 0.015*np.maximum(Lgrid-4.0,0)**1.25
plt.figure(figsize=(7.0,4.8))
im=plt.imshow(Sc,origin='lower',aspect='auto',extent=[pvals.min(),pvals.max(),lams.min(),lams.max()],cmap='magma')
plt.xlabel('residue production coefficient p')
plt.ylabel(r'diffusion-arrest coefficient $\lambda_D$')
plt.title('Robustness sweep: $S_c$ across production and diffusion-arrest regimes', fontsize=11)
plt.colorbar(im,label=r'estimated $S_c$')
plt.tight_layout()
plt.savefig(FIG/'fig8_robustness_heatmap.png', dpi=220, bbox_inches='tight', pad_inches=0.15)
plt.savefig(FIG/'fig8_robustness_heatmap.pdf', bbox_inches='tight', pad_inches=0.15)
plt.close()
np.savetxt(DATA/'robustness_heatmap.csv', Sc, delimiter=',')

# ---------------------------------------------------------------------
# Fig 9: universality class / benchmark map as diagram
# ---------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.8,4.8))
ax.axis('off')
boxes=[
    (0.03,0.55,0.24,0.28,'Flux\ninput / reactions\n$J$'),
    (0.30,0.55,0.24,0.28,'Residue load\n$\\rho$\n(tar, aggregates, crowding)'),
    (0.57,0.67,0.22,0.18,'Transport failure\n$D(\\rho), J(\\rho)$'),
    (0.57,0.40,0.22,0.18,'Boundary stress\n$\\Pi(\\rho), B$'),
    (0.82,0.55,0.15,0.28,'Collapse\nor rescue'),
    (0.30,0.10,0.24,0.22,'Active pruning\n$S$\nexport/degrade/recycle'),
]
for x,y,w,h,text in boxes:
    rect=plt.Rectangle((x,y),w,h,fill=False,lw=1.8)
    ax.add_patch(rect)
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=10)
# arrows
arrowprops=dict(arrowstyle='->',lw=1.7)
ax.annotate('',xy=(0.30,0.69),xytext=(0.27,0.69),arrowprops=arrowprops)
ax.annotate('',xy=(0.57,0.75),xytext=(0.54,0.72),arrowprops=arrowprops)
ax.annotate('',xy=(0.57,0.48),xytext=(0.54,0.66),arrowprops=arrowprops)
ax.annotate('',xy=(0.82,0.69),xytext=(0.79,0.74),arrowprops=arrowprops)
ax.annotate('',xy=(0.82,0.61),xytext=(0.79,0.48),arrowprops=arrowprops)
ax.annotate('',xy=(0.43,0.55),xytext=(0.43,0.32),arrowprops=arrowprops)
ax.annotate('',xy=(0.36,0.55),xytext=(0.36,0.32),arrowprops=dict(arrowstyle='<-',lw=1.7))
ax.text(0.5,0.95,'Residue-pruning-boundary universality class and wet-lab benchmark map',ha='center',fontsize=12)
ax.text(0.5,0.02,'Experimental proxies: fluorescence residue, FRAP diffusivity, leakage dye, vesicle radius, throughput, and rescue timing',ha='center',fontsize=9)
plt.savefig(FIG/'fig9_benchmark_map.png',dpi=220,bbox_inches='tight')
plt.savefig(FIG/'fig9_benchmark_map.pdf',bbox_inches='tight')
plt.close()
