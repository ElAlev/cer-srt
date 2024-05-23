import time
import os
import string
#import numpy.random as rd
import subprocess
import sys

from scripts.stock_markets import TEST_NAME

TESTS = ['Time', "Memory"]
WIN_LENGTH = [100, 200, 300, 400, 500, 1000, 10000]
ITERATIONS = 3
TIMEOUTS = [60]
SYSTEMS = ['sase', 'wayeb', 'flink', 'esper8']
TEST_NAME = 'taxiReg'
CONSUME = False
PRINT = False
POSTPROCESS = True
NUM_EVENT_DICT = {}
WORKING_FOLDER = '/path/to/my/local/folder'
LIMIT = -1
QUERIES = [1, 2, 3, 4]
FSM_MODEL = 'nsra'
WAYEB_OPT = 'true'
max_events = 585762

def create_folder():
    os.mkdir(f'{WORKING_FOLDER}/results/{TEST_NAME}')


def create_queries():
    print('Creating queries...')
    for system in SYSTEMS:
        if system == 'sase':
            create_sase_query()
        elif system == 'wayeb':
            create_wayeb_query()
        elif system == 'esper8':
            create_esper_query()
    print('Finished creating queries.')


def create_sase_query():
    os.mkdir(f'{WORKING_FOLDER}/results/{TEST_NAME}/sase')
    for i in QUERIES:
        with open(f'{WORKING_FOLDER}/taxiqueries/SASE/reg{i}.query') as tf:
            original = tf.read()
        for win_length in WIN_LENGTH:
            with open(f'{WORKING_FOLDER}/results/{TEST_NAME}/sase/sase_taxi_reg{i}_{win_length}.query', 'w') as tf:
                #sasewl = int(win_length / 10)
                tf.write(original.replace('TIMESTAMP', f'{win_length - 1}'))

def create_wayeb_query():
    os.mkdir(f'{WORKING_FOLDER}/results/{TEST_NAME}/wayeb')
    for i in QUERIES:
        with open(f'{WORKING_FOLDER}/taxiqueries/WAYEB/reg{i}.sre') as tf:
            original = tf.read()
        for win_length in WIN_LENGTH:
            with open(f'{WORKING_FOLDER}/results/{TEST_NAME}/wayeb/wayeb_taxi_reg{i}_{win_length}.sre', 'w') as tf:
                tf.write(original.replace('TIMESTAMP', f'{win_length}'))


def create_esper_query():
    os.mkdir(f'{WORKING_FOLDER}/results/{TEST_NAME}/esper')
    for i in QUERIES:
        with open(f'{WORKING_FOLDER}/taxiqueries/ESPER/reg{i}.query') as tf:
            original = tf.read()
        for win_length in WIN_LENGTH:
            with open(f'{WORKING_FOLDER}/results/{TEST_NAME}/esper/esper_taxi_reg{i}_{win_length}.query', 'w') as tf:
                tf.write(original.replace('TIMESTAMP', f'{win_length}'))


def run_systems():
    print('Running systems...')
    if not os.path.exists(f'{WORKING_FOLDER}/results/{TEST_NAME}/results'):
        os.mkdir(f'{WORKING_FOLDER}/results/{TEST_NAME}/results')
    for test in TESTS:
        print(f'Running {test} test...')
        for query in QUERIES:
            for system in SYSTEMS:
                print(f'Running {system}...')
                memorytest = False
                if test == 'Memory':
                    memorytest = True
                for win_length in WIN_LENGTH:
                    for j in range(len(TIMEOUTS)):
                        timeout = TIMEOUTS[j]
                        for i in range(ITERATIONS):
                            try:
                                if system == 'sase':
                                    print(
                                        f'Running sase with query sase_taxi_reg{query}_{win_length}.query, stream taxi.stream. Memorytest: {memorytest}')
                                    t0 = time.time_ns()
                                    res = run_sase(win_length, query, memorytest, timeout, max_events)
                                    total_time = time.time_ns() - t0
                                elif system == 'wayeb':
                                    print(
                                        f'Running wayeb with query wayeb_taxi_reg{query}_{win_length}.sre, stream taxi.stream. Memorytest: {memorytest}')
                                    t0 = time.time_ns()
                                    res = run_wayeb(win_length, query, memorytest, timeout)
                                    total_time = time.time_ns() - t0
                                elif system == 'esper8':
                                    print(
                                        f'Running esper8 with query esper_taxi_reg{query}_{win_length}.query, stream taxi.stream. Memorytest: {memorytest}')
                                    t0 = time.time_ns()
                                    res = run_esper8(win_length, query, memorytest, timeout, max_events)
                                    total_time = time.time_ns() - t0
                                elif system == 'flink':
                                    print(
                                        f'Running flink with query flink_taxi_reg{query}_{win_length}.query, stream taxi.stream. Memorytest: {memorytest}')
                                    t0 = time.time_ns()
                                    res = run_flink(win_length, query, memorytest, timeout, max_events)
                                    total_time = time.time_ns() - t0
                                else:
                                    continue
                                with open(f'{WORKING_FOLDER}/results/{TEST_NAME}/results/{system}_taxi_reg{query}_{win_length}_{test}.query' + '_out.txt', 'ab') as tf:
                                    if not j and not i:
                                        if memorytest:
                                            tf.write(
                                                b'MAXTotal,AVGTotal,MAXUsed,AVGUsed,Measurements\n')
                                        else:
                                            tf.write(
                                                b'Timeout,TotalTime,NumberOfEvents,EnumTime,Matches,ExecTime,ThroughputExec,ThroughputEnum\n')
                                    if not memorytest:
                                        tf.write(f'{timeout},'.encode())
                                    tf.write(res.stdout)
                                with open(f'{WORKING_FOLDER}/results/{TEST_NAME}/results/{system}_taxi_reg{query}_{win_length}_{test}.query' + '_err.txt', 'ab') as tf:
                                    tf.write(res.stderr)
                                print(
                                    f'successfully ran {system} query {system}_taxi_reg{query}_{win_length}.query with stream taxi.stream.')
                            except subprocess.TimeoutExpired as err:
                                with open(f'{WORKING_FOLDER}/results/{TEST_NAME}/results/{system}_taxi_reg{query}_{win_length}_{test}.query' + '_except.txt', 'a') as tf:
                                    tf.write('query timeout:\n')
                                    tf.write(str(err.timeout))
                                    tf.write('\n')
                                    tf.write(str(err.cmd))
                                    tf.write('\n')
                                    if (err.output != None):
                                        tf.write(err.output.decode())
                                    tf.write('\n')
                                    if (err.stderr != None):
                                        tf.write(err.stderr.decode())
                                    break
                            except subprocess.CalledProcessError as err:
                                with open(f'{WORKING_FOLDER}/results/{TEST_NAME}/results/{system}_taxi_reg{query}_{win_length}_{test}.query' + '_except.txt', 'a') as tf:
                                    tf.write('query error:\n')
                                    tf.write(str(err.returncode))
                                    tf.write('\n')
                                    tf.write(str(err.cmd))
                                    tf.write('\n')
                                    if (err.output != None):
                                        tf.write(err.output.decode())
                                    tf.write('\n')
                                    if (err.stderr != None):
                                        tf.write(err.stderr.decode())
                                    break
                            except Exception as err:
                                with open(f'{WORKING_FOLDER}/results/{TEST_NAME}/results/{system}_taxi_reg{query}_{win_length}_{test}.query' + '_except.txt', 'a') as tf:
                                    tf.write('query error:\n')
                                    tf.write(str(err))
                                    break
            print(f'Finished running {system}.')
        print(f'Finished running {test} test...')
    print('Finished Running systems.')



def run_sase(win_length, query, memorytest, timeout, max_events):
    return subprocess.run(['java', '-Xmx50G',
                           '-jar', f'{WORKING_FOLDER}/jars/sase.jar',
                           f'{WORKING_FOLDER}/results/{TEST_NAME}/sase/sase_taxi_reg{query}_{win_length}.query',
                           f'{WORKING_FOLDER}/taxistream/taxi.stream',
                           f'{CONSUME}', f'{memorytest}', f'{True}', f'{PRINT}', f'{max_events}', f'{3}', f'{timeout}', f'{POSTPROCESS}'],
                          timeout=timeout * 10, capture_output=True, check=True)

def run_wayeb(win_length, query, memorytest, timeout):
    subprocess.run(['java', '-Xmx50G',
                    '-jar', f'{WORKING_FOLDER}/jars/wayeb.jar',
                    'compile',
                    f'--patterns:{WORKING_FOLDER}/results/{TEST_NAME}/wayeb/wayeb_taxi_reg{query}_{win_length}.sre',
                    f'--fsmModel:{FSM_MODEL}',
                    f'--outputFsm:{WORKING_FOLDER}/results/{TEST_NAME}/wayeb/wayeb_taxi_reg{query}_{win_length}.fsm'],
                    timeout=timeout * 10, capture_output=False, check=True)
    return subprocess.run(['java', '-Xmx50G',
                           '-jar', f'{WORKING_FOLDER}/jars/wayeb.jar',
                           'recognition',
                           f'--fsm:{WORKING_FOLDER}/results/{TEST_NAME}/wayeb/wayeb_taxi_reg{query}_{win_length}.fsm',
                           f'--fsmModel:{FSM_MODEL}',
                           f'--stream:{WORKING_FOLDER}/taxistream/taxi.stream',
                           '--domainSpecificStream:taxi',
                           '--streamArgs:',
                           f'--statsFile:{WORKING_FOLDER}/results/{TEST_NAME}/wayeb/{query}_{win_length}.stats',
                           f'--reset:{CONSUME}',
                           f'--opt:{WAYEB_OPT}',
                           '--warmupFirst:false',
                           '--warmupStreamSize:400000',
                           '--findWarmupLimit:false',
                           '--batchLength:10000',
                           '--measurements:10',
                           f'--show:{PRINT}',
                           f'--postProcess:{POSTPROCESS}',
                           f'--timeout:{timeout}',
                           f'--mem:{memorytest}'],
                          timeout=timeout * 10, capture_output=True, check=True)

def run_esper8(win_length, query, memorytest, timeout, max_events):
    return subprocess.run(['java', '-Xmx50G',
                           '-jar', f'{WORKING_FOLDER}/jars/esper.jar',
                           'taxi',
                           f'{WORKING_FOLDER}/results/{TEST_NAME}/esper/esper_taxi_reg{query}_{win_length}.query',
                           f'{WORKING_FOLDER}/taxistream/taxi.stream',
                           f'{memorytest}', f'{True}', f'{max_events}', f'{timeout}', f'{PRINT}', f'{POSTPROCESS}', f'{LIMIT}'],
                          timeout=timeout * 10, capture_output=True, check=True)

def run_flink(win_length, query, memorytest, timeout, max_events):
    return subprocess.run(['java', '-Xmx50G',
                           '-jar', f'{WORKING_FOLDER}/jars/flink.jar',
                           'taxi',
                            f'{WORKING_FOLDER}/taxistream/taxi.stream',
                            f'reg{query}', f'{win_length}', 'false', f'{timeout}', f'{memorytest}', f'{max_events}', f'{PRINT}', f'{POSTPROCESS}', f'{LIMIT}', f'{CONSUME}'],
                          timeout=timeout * 10, capture_output=True, check=True)

def main():
    print(f'Starting test with TEST_NAME {TEST_NAME}')
    create_folder()
    create_queries()
    run_systems()


if __name__ == "__main__":
    main()
