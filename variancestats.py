# THIS CODE IS OBSOLETE. This code computes variance on MNI-transformed images. For some reason, this results in variations outside the field of view. In the new implementation, the variance is computed in the subject-specific functional space as part of the calcseedconn and seedconn2mni routines of the pipeline.

# this code computes variance for each subject pre and post retroicor, and then compares variance pre and post at group level

import nibabel,sys
import numpy as np
import scipy.stats
import statsmodels.stats.multitest as mtest

p_thresh=0.05


def calcvariance(ifile,ofile):
    
    img_nib=nibabel.load(ifile)
    img=img_nib.get_data()
    affine=img_nib.affine # used to save the result in a NIFTI file
    
    imgreshape=img.reshape((np.prod(img.shape[0:3]),img.shape[3]))
    
    v=np.var(imgreshape,axis=1)

    # write v to file
    v=np.reshape(v,(img.shape[0],img.shape[1],img.shape[2]))
    onifti = nibabel.nifti1.Nifti1Image(v,affine)
    onifti.to_filename(ofile)    
    


def prepostmatchedpairst(prespmfiles,postspmfiles,ofile):
    
    n=len(prespmfiles)
    
    # the following just to get the size of the SPMs
    img_nib=nibabel.load(prespmfiles[0])
    img=img_nib.get_data()
    affine=img_nib.affine # used to save the result in a NIFTI file

    paireddiff=np.zeros((n,np.prod(img.shape)))
    t=np.zeros((1,np.prod(img.shape)))    
    p=np.zeros((1,np.prod(img.shape)))
    
    for i in np.arange(n):
        spm1_nib=nibabel.load(prespmfiles[i])
        spm1=spm1_nib.get_data()
        spm1=spm1.reshape((1,np.prod(spm1.shape)))
        
        spm2_nib=nibabel.load(postspmfiles[i])
        spm2=spm2_nib.get_data()
        spm2=spm2.reshape((1,np.prod(spm2.shape)))
        
        paireddiff[i,:]=spm2-spm1
         
    (t,p)=scipy.stats.ttest_1samp(paireddiff,0.0)
    
    # adjust for multiple comparisons    
    p_fdr=mtest.multipletests(p,p_thresh,'fdr_bh')    
    #t[~p_fdr[0]]=0
    t[p>0.05]=np.nan

    # write t to file
    t=np.reshape(t,(img.shape[0],img.shape[1],img.shape[2]))
    onifti = nibabel.nifti1.Nifti1Image(t,affine)
    onifti.to_filename(ofile)

        
# dictionary of corresponding sessions for healthy volunteer data set
# sessions.keys() gives you all subject IDs
# multiple sessions per subject are added to the lists on the right
sessions=dict()
sessions['7130']=['20140312']
sessions['7934']=['20140207']
sessions['9910']=['20140204']
#sessions['10577']=['20140325']
#sessions['10649']=['20140316']
#sessions['11164']=['20140316']
#sessions['11308']=['20140304']
#sessions['11494']=['20140311']
#sessions['11515']=['20140305']
#sessions['11570']=['20140310']
#sessions['11672']=['20140318']

basepath='/data/klymene/chen_lab/mkayvanrad/data/original/healthyvolunteer/processed/retroicorpipe'

outputfile=basepath+'/prepostvariancematchedpairst.nii.gz'

prefiles=[]
postfiles=[]
spmfiles=[]

for subj in sessions.keys():
    for sess in sessions[subj]:
        ifile=basepath+'/'+subj+'/'+sess+'/fepi/fepi_pipeline_noRet_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_tomni152.nii.gz'
        ofile=basepath+'/'+subj+'/'+sess+'/fepi/fepi_pipeline_noRet_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_tomni152_var.nii.gz'
        calcvariance(ifile,ofile)
        prefiles.append(ofile)
        
        ifile=basepath+'/'+subj+'/'+sess+'/fepi/fepi_pipeline_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_retroicor_tomni152.nii.gz'
        ofile=basepath+'/'+subj+'/'+sess+'/fepi/fepi_pipeline_slicetimer_mcflirt_brainExtractAFNI_ssmooth_3dFourier_retroicor_tomni152_var.nii.gz'
        calcvariance(ifile,ofile)
        postfiles.append(ofile)
        
prepostmatchedpairst(prefiles,postfiles,outputfile)


