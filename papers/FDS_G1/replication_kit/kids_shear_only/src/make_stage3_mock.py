from pathlib import Path
import numpy as np, pandas as pd, yaml, shutil, json, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from stage3_lensing_3x2pt import Stage3Lensing3x2ptLikelihood
base=Path(__file__).resolve().parent/'stage3_mock'
data=base/'data'
data.mkdir(parents=True, exist_ok=True)
# simple normalized redshift distributions
def nz_gauss(z, mu, sig):
    y=np.exp(-0.5*((z-mu)/sig)**2)
    y[z<=0]=0
    return y
z=np.linspace(0.001,2.0,300)
for name,mu,sig in [('source_0',0.65,0.18),('source_1',1.0,0.22),('lens_0',0.35,0.10),('lens_1',0.65,0.13)]:
    pd.DataFrame({'z':z,'nz':nz_gauss(z,mu,sig)}).to_csv(data/f'nz_{name}.csv',index=False)
# data vector rows, compact smoke test
rows=[]
for th in [5.0,20.0,80.0]:
    rows.append(('xip','src0','src0',th,0.0))
    rows.append(('xim','src0','src0',th,0.0))
    rows.append(('gammat','lens0','src0',th,0.0))
    rows.append(('wtheta','lens0','lens0',th,0.0))
df=pd.DataFrame(rows,columns=['kind','bin1','bin2','theta_arcmin','value'])
df.to_csv(data/'vector.csv',index=False)
# crude covariance, will overwrite after theory magnitude known
np.savetxt(data/'cov.txt',np.eye(len(df))*1e-12)
# rbh table fallback-ish smooth shape but explicit table
avec=np.linspace(0.05,1.0,200)
R=4*(avec**1.4)*(1-0.35*avec)
R=R/np.max(R)
pd.DataFrame({'a':avec,'R_bH':R}).to_csv(data/'rbh.csv',index=False)
cfg={
 'data_vector_csv':'data/vector.csv', 'covariance_txt':'data/cov.txt', 'rbh_table':'data/rbh.csv',
 'z_min':0.001,'z_max':2.0,'nz_grid':120,'ell_min':5.0,'ell_max':2000.0,'nell':120,
 'theta_grid_arcmin':[5,20,80],
 'vary_lens_bias':True,'lens_bias_bounds':[0.5,3.0],
 'vary_shear_m':False,
 'sources':[{'name':'src0','nz_file':'data/nz_source_0.csv','m':0.0},{'name':'src1','nz_file':'data/nz_source_1.csv','m':0.0}],
 'lenses':[{'name':'lens0','nz_file':'data/nz_lens_0.csv','bias':1.4},{'name':'lens1','nz_file':'data/nz_lens_1.csv','bias':1.7}],
}
with open(base/'config.yaml','w') as f: yaml.safe_dump(cfg,f)
# instantiate and generate m34 mock values
like=Stage3Lensing3x2ptLikelihood(base/'config.yaml')
names=like.param_names('m34')
pars={'Omega_m':0.30,'h':0.68,'Omega_b':0.049,'sigma8':0.80,'n_s':0.965,'s':2.55,'b_lens0':1.4,'b_lens1':1.7}
theta=[pars[n] for n in names]
pred=like.predict_vector('m34',theta)
# Avoid tiny zero errors; set 15% relative plus floor covariance
data_vals=pred.copy()
df['value']=data_vals
df.to_csv(data/'vector.csv',index=False)
sig=np.maximum(np.abs(data_vals)*0.15, np.nanmax(np.abs(data_vals))*0.02 + 1e-12)
# add mild correlations
cov=np.diag(sig**2)
for i in range(len(sig)):
  for j in range(len(sig)):
    if i!=j:
      cov[i,j]=0.05*sig[i]*sig[j]
np.savetxt(data/'cov.txt',cov)
print(json.dumps({'base':str(base),'nrows':len(df),'param_names':names,'theta':theta,'pred_minmax':[float(np.min(pred)),float(np.max(pred))]},indent=2))
