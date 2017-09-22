import workflow
from pipeline import Pipeline
from preprocessingstep import PreprocessingStep
import fileutils
import preprocessingstep
import sys, getopt, os
import copy

subjectsfiles=[]
combs=[]
addsteps=True
runpipesteps=[] # this is a list
optimalpipesteps=[] # this is a list of lists
fixedpipesteps=[] # this is a list
showpipes=False
resout=''

#mni152='/usr/share/data/fsl-mni152-templates/MNI152lin_T1_2mm_brain' # this can be got as an input

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'hp:s:',\
                                ['help','pipeline=', 'subjects=', 'perm=', 'onoff=', 'const=', 'add', 'combine', 'fixed=', 'showpipes','mni152=','resout='])
except getopt.GetoptError:
    print('usage: testbench_workflow.py -p <pipeline text file> -s <subjects file>')
    sys.exit()
for (opt,arg) in opts:
    if opt in ('-h', '--help'):
        print('usage: testbench_workflow.py -p <pipeline text file> -s <subjects file>')
        sys.exit()
    elif opt in ('-p','--pipeline'):
        runpipesteps+=preprocessingstep.makesteps(arg)
    elif opt in ('--fixed'):
        fixedpipesteps+=preprocessingstep.makesteps(arg)
    elif opt in ('--perm'):
        steps=preprocessingstep.makesteps(arg)
        if addsteps:
            optimalpipesteps+=list(preprocessingstep.permutations(steps))
        else:
            optimalpipesteps=list(preprocessingstep.concatstepslists(optimalpipesteps,\
                                                                     list(preprocessingstep.permutations(steps))))
    elif opt in ('--onoff'):
        steps=preprocessingstep.makesteps(arg)
        if addsteps:
            optimalpipesteps+=list(preprocessingstep.onoff(steps))
        else:
            optimalpipesteps=list(preprocessingstep.concatstepslists(optimalpipesteps,\
                                                                     list(preprocessingstep.onoff(steps))))
    elif opt in ('--const'):
        steps=preprocessingstep.makesteps(arg)
        if addsteps:
            optimalpipesteps+=[steps]
        else:
            optimalpipesteps=list(preprocessingstep.concatstepslists(optimalpipesteps,[steps]))
    elif opt in ('-s','--subjects'):
        subjectsfiles.append(arg)
    elif opt in ('--add'):
        addsteps=True
    elif opt in ('--combine'):
        addsteps=False
    elif opt in ('--showpipes'):
        showpipes=True
    elif opt in ('--mni152'):
        mni152=arg
    elif opt in ('--resout'):
        resout=arg

# just for myself. remove for distribution.        
if resout=='':
    sys.exit('Give resout you idiot!!')
        
envvars=workflow.EnvVars()
envvars.mni152=mni152
        
# run workflow
if len(runpipesteps)>0:
    runwf=workflow.Workflow('Run Pipe')
    subjects=[]
    for sfile in subjectsfiles:
        subjects=subjects+workflow.getsubjects(sfile)
    for subj in subjects:
        for sess in subj.sessions:
            for run in sess.runs:
                pipe=Pipeline('runpipe',runpipesteps)
                pipe.setibase(run.data.bold)
                pipe.setobase(run.data.opath)
                pipe.setdata(run.data) # when running pipeline do not deepcopy so that results, e.g., motpar, can be recorded if needed
                pipe.setenvvars(envvars)
                run.addpipeline(pipe)
        runwf.addsubject(subj)

# optimal workflow
if len(optimalpipesteps)>0:
    optimalwf=workflow.Workflow('Optimal Pipe')
    subjects=[]
    for sfile in subjectsfiles:
        subjects=subjects+workflow.getsubjects(sfile)
    for subj in subjects:
        for sess in subj.sessions:
            for run in sess.runs:
                count=0
                for steps in optimalpipesteps:
                    count=count+1
                    pipe=Pipeline('pipe'+str(count),steps)
                    pipe.setibase(run.data.bold)
                    pipe.setobase(run.data.opath)
                    pipe.setdata(copy.deepcopy(run.data))
                    pipe.setenvvars(envvars)
                    run.addpipeline(pipe)
        optimalwf.addsubject(subj)
# fixed workflow
if len(fixedpipesteps)>0:
    fixedwf=workflow.Workflow('Fixed Pipe')
    subjects=[]
    for sfile in subjectsfiles:
        subjects=subjects+workflow.getsubjects(sfile)
    for subj in subjects:
        for sess in subj.sessions:
            for run in sess.runs:
                pipe=Pipeline('fixedpipe',fixedpipesteps)
                pipe.setibase(run.data.bold)
                pipe.setobase(run.data.opath)
                pipe.setdata(copy.deepcopy(run.data))
                pipe.setenvvars(envvars)
                run.addpipeline(pipe)
        fixedwf.addsubject(subj)


if showpipes:
    # print all pipelines run
    if len(runpipesteps)>0:
        print('-----')
        print('-----')
        print('Pipeline runned:')
        for subj in [runwf.subjects[0]]:
            for sess in [subj.sessions[0]]:
                for run in [sess.runs[0]]:
                    for pipe in run.pipelines:
                        #print(subj.ID,'_',sess.ID,'_',run.seqname, pipe.getsteps())
                        print(run.seqname, pipe.getsteps())    
    # print fixed pipelines
    if len(fixedpipesteps)>0:
        print('-----')
        print('-----')    
        print('Fixed pipelines:')
        for subj in [fixedwf.subjects[0]]:
            for sess in [subj.sessions[0]]:
                for run in [sess.runs[0]]:
                    for pipe in run.pipelines:
                        #print(subj.ID,'_',sess.ID,'_',run.seqname, pipe.getsteps())
                        print(run.seqname, pipe.getsteps())    
    # print optimized pipelines
    if len(optimalpipesteps)>0:
        print('-----')
        print('-----')    
        print('Otimized pipelines:')
        for subj in [optimalwf.subjects[0]]:
            for sess in [subj.sessions[0]]:
                for run in [sess.runs[0]]:
                    for pipe in run.pipelines:
                        #print(subj.ID,'_',sess.ID,'_',run.seqname, pipe.getsteps())
                        print(run.seqname, pipe.getsteps())
    sys.exit()
    
# now process    
if len(runpipesteps)>0:
    runwf.process()
if len(optimalpipesteps)>0:
    seqname=optimalwf.subjects[0].sessions[0].runs[0].seqname # pick the 1st subject's 1st session's 1st run's sequnce
    optimalwf.computebetweensubjectreproducibility(seqname)
if len(fixedpipesteps)>0:
    seqname=fixedwf.subjects[0].sessions[0].runs[0].seqname # pick the 1st subject's 1st session's 1st run's sequnce
    fixedwf.computebetweensubjectreproducibility(seqname)

# save the results
if len(optimalpipesteps)>0:
    optimalwf.saveallpipes(resout+'_optimalwf_allpipes.csv')
    optimalwf.saveoptimalpipes(resout+'_optimalwf_optimalpipes.csv')
    optimalwf.savebetweensubjectreproducibility_r(resout+'_optimalwf_betsubjrep_r.csv')
    optimalwf.savebetweensubjectreproducibility_j(resout+'_optimalwf_betsubjrep_j.csv')
    optimalwf.savebetweensubjectreproducibility_rj(resout+'_optimalwf_betsubjrep_rj.csv')
    optimalwf.savebetweensubjectoverlap_r(resout+'_optimalwf_betsubjolap_r.csv')
    optimalwf.savebetweensubjectoverlap_j(resout+'_optimalwf_betsubjolap_j.csv')
    optimalwf.savebetweensubjectoverlap_rj(resout+'_optimalwf_betsubjolap_rj.csv')
    
if len(fixedpipesteps)>0:
    fixedwf.saveallpipes(resout+'_fixedwf_allpipes.csv')
    fixedwf.saveoptimalpipes(resout+'_fixedwf_optimalpipes.csv')
    fixedwf.savebetweensubjectreproducibility_r(resout+'_fixedwf_betsubjrep_r.csv')
    fixedwf.savebetweensubjectreproducibility_j(resout+'_fixedwf_betsubjrep_j.csv')
    fixedwf.savebetweensubjectreproducibility_rj(resout+'_fixedwf_betsubjrep_rj.csv')
    fixedwf.savebetweensubjectoverlap_r(resout+'_fixedwf_betsubjolap_r.csv')
    fixedwf.savebetweensubjectoverlap_j(resout+'_fixedwf_betsubjolap_j.csv')
    fixedwf.savebetweensubjectoverlap_rf(resout+'_fixedwf_betsubjolap_rj.csv')



