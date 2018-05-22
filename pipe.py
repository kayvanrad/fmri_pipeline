#!/usr/bin/env python

def printhelp():
    print('USAGE:')
    print('pipe.py  --subjects <subjects file> --pipeline <pipeline file> --perm <pipeline file> --onoff <pipeline file> --const <pipeline file> --add --combine --fixed <pipeline file> --showpipes --template <template file> --resout <base name>')
    print('ARGUMENTS:')
    print('--subjects <subj file>: specify subjects file (required)')
    print('--pipeline <pipe file>: specify a pipeline file to be run on all subjects without optimization and/or calculation of between subject metrics')
    print('--const <pipe file>: specify a pipeline file to be used to form constant section of the optimized pipeline')
    print('--perm <pipe file>: specify a pipeline file to be used to form permutations section of the optimized pipeline')
    print('--onoff <pipe file>: specify a pipeline file to be used to form on/off section of the optimized pipeline')
    print('--permonoff <pipe file>: on/off combinations and their permutations')
    print('--select <pipe file>: select one step from the pipe file at a time')
    print('--combine: flag specifying that all new (permutation/on-off/constant) steps are combined with the previous ones from this point on (Default) (See example below)')
    print('--add: flag specifying that all new (permutation/on-off/constant) steps are added to the previous pipelines from this point on (Default is combine) (See example below)')
    print('--fixed <pipe file>: specify a fixed pipeline for the calculation of between subject metrics')
    print('--showpipes: show all pipelines to be run/optimized/validated without running. Only use to see a list of pipelines to be run/optimized. This will NOT run/optimize the pipelines. Remove the flag to run/optimize.')
    print('--template <temp file>: template file to be used for between subject calculations, e.g., MNI template. Required with --perm, --onoff, --const, --fixed, unless using --showpipes.')
    print('--resout <base name>: base path/name to save results in csv format. Extension (.csv) and suffixed are added to the base name.')
    print('--parcellate: parcellate the output of the run/optimal/fixed pipeline(s).')
    print('--meants: compute mean time series over CSF, GM, and WM for the pipeline output. This automatically parcellates the output. If used with --seedconn, mean time series over the network is also computed.')
    print('--seedconn: compute seed-connectivity network on the pipeline output. Need to provide a seed file in subjects file.')
    print('--tomni: transform pipeline output and seed connectivity (if used --seedconn) to standard MNI space.')
    print('--keepintermed: keep results of the intermediate steps')
    print('--boldregdof <dof>: degrees of freedom to be used for bold registration (Default = 12).')
    print('--structregdof <dof>: degrees of freedom to be used for structural registration (Default = 12).')
    print('--boldregcost <cost function>: cost fuction to be used for bold registration (Default = \'corratio\').')
    print('--structregcost <cost function>: cost fuction to be used for structural registration (Default = \'corratio\').')
    print('--runpipename <name>: prefix to precede name of steps in the run pipeline output files. (Default=\'\')')
    print('--fixpipename <name>: prefix to precede name of steps in the fixed pipeline output files. (Default=\'fix\')')
    print('--optpipename <name>: prefix to precede name of steps in the optimal pipeline output files. (Default=\'opt\')')
    print('--outputsubjects <subj file>: specify a subject file, which is populated based on the results of the pipeline run on all subjects. Only applicable with --pipeline.')
    print('--showsubjects: print the list of all subjects to be processed and exit.')
    print('Report bugs/issues to M. Aras Kayvanrad (mkayvanrad@research.baycrest.org)')


import workflow
from pipeline import Pipeline
from preprocessingstep import PreprocessingStep
import fileutils
import preprocessingstep
import sys, getopt, os
import copy

subjectsfiles=[]
combs=[]
addsteps=False
runpipesteps=[] # this is a list
optimalpipesteps=[] # this is a list of lists
fixedpipesteps=[] # this is a list
showpipes=False
resout=''
parcellate=False
meants=False
seedconn=False
tomni=False
runpipename=''
optpipename='opt'
fixpipename='fix'
outputsubjectsfile=''
keepintermed=False
runpipe=False
showsubjects=False

envvars=workflow.EnvVars()

# parse command-line arguments
try:
    (opts,args) = getopt.getopt(sys.argv[1:],'h',\
                                ['help','pipeline=', 'subjects=', 'perm=', 'onoff=', 'permonoff=', 'const=', 'select=', 'add', 'combine', 'fixed=', 'showpipes', 'template=', 'resout=', 'parcellate', 'meants', 'seedconn', 'tomni', 'boldregdof=', 'structregdof=', 'boldregcost=', 'structregcost=', 'outputsubjects=', 'keepintermed', 'runpipename=', 'fixpipename=', 'optpipename=','showsubjects'])
except getopt.GetoptError:
    printhelp()
    sys.exit()
for (opt,arg) in opts:
    if opt in ('-h', '--help'):
        printhelp()
        sys.exit()
    elif opt in ('--pipeline'):
        runpipesteps+=preprocessingstep.makesteps(arg)
        runpipe=True
        #(directory,namebase)=os.path.split(arg)
        #namebase=fileutils.removext(namebase)
        #runpipename+=namebase
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

    elif opt in ('--permonoff'):
        steps=preprocessingstep.makesteps(arg)
        if addsteps:
            optimalpipesteps+=list(preprocessingstep.permonoff(steps))
        else:
            optimalpipesteps=list(preprocessingstep.concatstepslists(optimalpipesteps,\
                                                                     list(preprocessingstep.permonoff(steps))))

    elif opt in ('--select'):
        steps=preprocessingstep.makesteps(arg)
        if addsteps:
            optimalpipesteps+=list(preprocessingstep.select(steps))
        else:
            optimalpipesteps=list(preprocessingstep.concatstepslists(optimalpipesteps,\
                                                                     list(preprocessingstep.select(steps))))
        
    elif opt in ('--const'):
        steps=preprocessingstep.makesteps(arg)
        if addsteps:
            optimalpipesteps+=[steps]
        else:
            optimalpipesteps=list(preprocessingstep.concatstepslists(optimalpipesteps,[steps]))
    elif opt in ('--subjects'):
        subjectsfiles.append(arg)
    elif opt in ('--add'):
        addsteps=True
    elif opt in ('--combine'):
        addsteps=False
    elif opt in ('--showpipes'):
        showpipes=True
    elif opt in ('--template'):
        envvars.mni152=arg
    elif opt in ('--resout'):
        resout=arg
    elif opt in ('--parcellate'):
        parcellate=True
    elif opt in ('--meants'):
        meants=True
    elif opt in ('--seedconn'):
        seedconn=True
    elif opt in ('--tomni'):
        tomni=True
    elif opt in ('--boldregdof'):
        envvars.boldregdof=arg
    elif opt in ('--structregdof'):
        envvars.structregdof=arg
    elif opt in ('--boldregcost'):
        envvars.boldregcost=arg
    elif opt in ('--structregcost'):
        envvars.structregcost=arg
    elif opt in ('--outputsubjects'):
        outputsubjectsfile=arg
    elif opt in ('--keepintermed'):
        keepintermed=True
    elif opt in ('--runpipename'):
        runpipename=arg
    elif opt in ('--fixpipename'):
        fixpipename=arg
    elif opt in ('--optpipename'):
        optpipename=arg
    elif opt in ('--showsubjects'):
        showsubjects=True

if subjectsfiles==[]:
    print('Please specify subjects file. Get help using -h or --help.')

if showsubjects:
    subjects=[]
    for sfile in subjectsfiles:
        subjects+=workflow.getsubjects(sfile)
    subjcount=0
    sesscount=0
    runcount=0
    for subj in subjects:
        subjcount += 1
        for sess in subj.sessions:
            sesscount += 1
            for run in sess.runs:
                runcount += 1
                print(subj.ID, sess.ID, run.data.bold, run.data.opath)
    print('Total # subjects =',subjcount)
    print('Total # sessions =',sesscount)
    print('Total # runs =', runcount)
    sys.exit()

# run workflow
if runpipe:
    subjects=[]
    for sfile in subjectsfiles:
        subjects+=workflow.getsubjects(sfile)
    runwf=workflow.Workflow('RunWF')
    for subj in subjects:
        for sess in subj.sessions:
            for run in sess.runs:
                run.data.envvars=envvars
                pipe=Pipeline(runpipename,runpipesteps)
                pipe.setibase(run.data.bold)
                pipe.setobase(run.data.opath)
                pipe.setdata(run.data) # when running pipeline do not deepcopy so that results can be recorded if needed
                pipe.keepintermed=keepintermed
                run.addpipeline(pipe)
        runwf.addsubject(subj)
    if parcellate:
        runwf.parcellate=True
    if seedconn:
        runwf.seedconn=True
    if meants:
        runwf.meants=True
    if tomni:
        runwf.tomni=True
        
# optimal workflow
if len(optimalpipesteps)>0:
    subjects=[]
    for sfile in subjectsfiles:
        subjects+=workflow.getsubjects(sfile)
    optimalwf=workflow.Workflow('OptWF')
    for subj in subjects:
        for sess in subj.sessions:
            for run in sess.runs:
                count=0
                run.data.envvars=envvars
                for steps in optimalpipesteps:
                    count=count+1
                    pipe=Pipeline(optpipename+'pipe'+str(count),steps)
                    pipe.setibase(run.data.bold)
                    pipe.setobase(run.data.opath)
                    pipe.setdata(copy.deepcopy(run.data))
                    pipe.keepintermed=keepintermed
                    run.addpipeline(pipe)
        optimalwf.addsubject(subj)
    if parcellate:
        optimalwf.parcellate=True
    if seedconn:
        optimalwf.seedconn=True
    if meants:
        optimalwf.meants=True
         
# fixed workflow
if len(fixedpipesteps)>0:
    subjects=[]
    for sfile in subjectsfiles:
        subjects+=workflow.getsubjects(sfile)
    fixedwf=workflow.Workflow('FixedWF')
    for subj in subjects:
        for sess in subj.sessions:
            for run in sess.runs:
                run.data.envvars=envvars
                pipe=Pipeline(fixpipename,fixedpipesteps)
                pipe.setibase(run.data.bold)
                pipe.setobase(run.data.opath)
                pipe.setdata(copy.deepcopy(run.data))
                pipe.keepintermed=keepintermed
                run.addpipeline(pipe)
        fixedwf.addsubject(subj)
    if parcellate:
        fixedwf.parcellate=True
    if seedconn:
        fixedwf.seedconn=True
    if meants:
        fixedwf.meants=True
        
if showpipes:
    # print all pipelines run
    if len(runpipesteps)>0:
        print('-----')
        print('-----')
        print('Pipeline run:')
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
        print('Optimized pipelines:')
        for subj in [optimalwf.subjects[0]]:
            for sess in [subj.sessions[0]]:
                for run in [sess.runs[0]]:
                    for pipe in run.pipelines:
                        #print(subj.ID,'_',sess.ID,'_',run.seqname, pipe.getsteps())
                        print(run.seqname, pipe.getsteps())
    sys.exit()
    
# now process    
if runpipe:
    runwf.run()
    if len(outputsubjectsfile)>0:
        workflow.savesubjects(outputsubjectsfile,runwf.subjects)

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
    fixedwf.savebetweensubjectoverlap_rj(resout+'_fixedwf_betsubjolap_rj.csv')




