from multiprocessing import Pool
from itertools import repeat
import subprocess, os
from pathlib import Path
from ..namedconf import render_command, to_dict

def create_env (expt):
    glb_env = os.environ.copy()

    er, run = expt.er, expt.run
    env = er.get_env(run)
    env = {name: value for name, value in env}
    glb_env.update(env)
    return glb_env

def create_job(expt, log_to_file):
    command = render_command(expt)
    command = command.strip().replace('\n','').replace('\t','').replace('\r','')
    cmds = [c for c in command.split(' ') if c != '']
    cmds_str = ' '.join(cmds)
    print (f'create_job: command = {cmds_str}')

    env = create_env(expt)
    out_dir = expt.run.output_dir
    os.makedirs(out_dir, exist_ok=True)
    assert Path(out_dir).exists()

    if log_to_file:
        log_fname = expt.run.output_log_file
        fp = open(log_fname, 'w', encoding='utf-8')
        print (f'Logging to file {log_fname}')
        stdout = fp
        stderr = subprocess.STDOUT
    else:
        stdout = subprocess.PIPE
        stderr = subprocess.PIPE


    #run.run_name, .max_memory
    result = subprocess.run(cmds, 
                    env=env, stdout=stdout, stderr=stderr)


    if log_to_file:
        fp.close()
    else:
        print ('stdout:')
        print (result.stdout.decode('utf-8'))
        print ('stderr:')
        print (result.stderr.decode('utf-8'))


def job_completed (result):
    print (f'completed: {result}')

def job_errored(result):
    print (f'error: {result}')

def dispatch_expts_process (expts, log_to_file=True):
    count = len(expts)
    args = zip(expts, repeat(log_to_file))

    with Pool(processes=count) as pool:
        #r = pool.starmap(create_job, zip(expts, repeat(log_to_file)))
        r = pool.starmap_async(create_job, args, callback=job_completed, error_callback=job_errored)
        r.wait()





