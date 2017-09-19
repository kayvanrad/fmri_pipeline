import workflow
from pipeline import Pipeline
from preprocessingstep import PreprocessingStep
import fileutils
import preprocessingstep
import sys, getopt, os

# dictionary of corresponding sessions for Healthy elderly data set
# sessions.keys() gives you all subject IDs
# multiple sessions per subject are added to the lists on the right
sessions=dict()
#sessions['11912']=['20170201']
#sessions['7397']=['20170213']
#sessions['6051']=['20170222']
sessions['13719']=['20170316']
sessions['4592']=['20170328']
'''sessions['10306']=['20170329']
sessions['8971']=['20170413']
sessions['12087']=['20170421']
sessions['12475']=['20170501']
sessions['10724']=['20170526']
sessions['7334']=['20170605']
sessions['14804']=['20170608']
sessions['7982']=['20170612']
sessions['12420']=['20170615']
sessions['8060']=['20170628']'''

basePath='/home/mkayvanrad/data/healthyelderly'

seqname='mbepi'

subjects=[]

for subj in sessions.keys():
    for sess in sessions[subj]:
        fileutils.createdir(basePath+'/'+subj+'/'+sess+'/processed/'+seqname)
        data=workflow.Data()
        data.bold=basePath+'/'+subj+'/'+sess+'/nii/mbepi.nii.gz'
        data.structural=basePath+'/'+subj+'/'+sess+'/processed/mprage_swp_brain.nii.gz'
        data.card=basePath+'/'+subj+'/'+sess+'/physio/siemens/3fmri102b'+subj+'.puls.1D'
        data.resp=basePath+'/'+subj+'/'+sess+'/physio/biopac/run3.resp.1D'
        data.opath=basePath+'/'+subj+'/'+sess+'/processed'+'/'+seqname+'/'+seqname
        data.connseed=basePath+'/'+subj+'/'+sess+'/processed/'+seqname+'/'+seqname+'_pcc_harvard-oxford.nii.gz'
        subject=workflow.Subject(subj)
        session=workflow.Session(sess)
        run=workflow.Run(seqname,data)
        session.addrun(run)
        subject.addsession(session)
        subjects.append(subject)
      
workflow.savesubjects(basePath+'/'+seqname+'_'+'subjects.txt',subjects)

