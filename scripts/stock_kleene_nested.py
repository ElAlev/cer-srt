import time
import os
import string
#import numpy.random as rd
import subprocess
import sys

TESTS = ['Time', 'Memory']
WIN_LENGTH = [500, 1000, 2000, 5000, 10000, 30000]
ITERATIONS = 3
TIMEOUTS = [60]
SYSTEMS = ['wayeb']
TEST_NAME = 'stockKleeneNested'
CONSUME = False # DO NOT CHANGE, Esper8 queries written with no consume
PRINT = False
POSTPROCESS = True
NUM_EVENT_DICT = {}
WORKING_FOLDER = '/path/to/my/local/folder'
LIMIT = -1
QUERIES = [1, 2, 3, 4]
FSM_MODEL = 'nsra'
WAYEB_OPT = 'true'
max_events = 224473


def create_folder():
    os.mkdir(f'{WORKING_FOLDER}/results/{TEST_NAME}')

def create_queries():
    print('Creating queries...')
    for system in SYSTEMS:
        if system =='wayeb':
            create_wayeb_query()
        elif system == 'esper8':
            create_esper_query()
    print('Finished creating queries.')


def create_wayeb_query():
    os.mkdir(f'{WORKING_FOLDER}/results/{TEST_NAME}/wayeb')
    for i in QUERIES:
        with open(f'{WORKING_FOLDER}/stockqueries/WAYEB/kn{i}.sre') as tf:
            original = tf.read()
        for win_length in WIN_LENGTH:
            with open(f'{WORKING_FOLDER}/results/{TEST_NAME}/wayeb/wayeb_stocks_kn{i}_{win_length}.sre', 'w') as tf:
                tf.write(original.replace('TIMESTAMP', f'{win_length}'))

def create_esper_query():
    os.mkdir(f'{WORKING_FOLDER}/results/{TEST_NAME}/esper')
    for i in QUERIES:
        with open(f'{WORKING_FOLDER}/stockqueries/ESPER/kn{i}.query') as tf:
            original = tf.read()
        for win_length in WIN_LENGTH:
            with open(f'{WORKING_FOLDER}/results/{TEST_NAME}/esper/esper_stocks_kn{i}_{win_length}.query', 'w') as tf:
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
                                if system == 'wayeb':
                                    print(
                                        f'Running wayeb with query wayeb_stocks_kn{query}_{win_length}.sre, stream stocks.stream. Memorytest: {memorytest}')
                                    t0 = time.time_ns()
                                    res = run_wayeb(win_length, query, memorytest, timeout, max_events)
                                    total_time = time.time_ns() - t0
                                elif system == 'esper8':
                                    print(
                                        f'Running esper8 with query esper_stocks_kn{query}_{win_length}.query, stream stocks.stream. Memorytest: {memorytest}')
                                    t0 = time.time_ns()
                                    res = run_esper8(win_length, query, memorytest, timeout, max_events)
                                    total_time = time.time_ns() - t0
                                else:
                                    sys.exit(1)
                                with open(f'{WORKING_FOLDER}/results/{TEST_NAME}/results/{system}_stocks_kn{query}_{win_length}_{test}.query' + '_out.txt', 'ab') as tf:
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
                                with open(f'{WORKING_FOLDER}/results/{TEST_NAME}/results/{system}_stocks_kn{query}_{win_length}_{test}.query' + '_err.txt', 'ab') as tf:
                                    tf.write(res.stderr)
                                print(
                                    f'successfully ran {system} query {system}_stocks_kn{query}_{win_length}.query with stream stocks.stream.')
                            except subprocess.TimeoutExpired as err:
                                with open(f'{WORKING_FOLDER}/results/{TEST_NAME}/results/{system}_stocks_kn{query}_{win_length}_{test}.query' + '_except.txt', 'a') as tf:
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
                                with open(f'{WORKING_FOLDER}/results/{TEST_NAME}/results/{system}_stocks_kn{query}_{win_length}_{test}.query' + '_except.txt', 'a') as tf:
                                    tf.write('query error (CalledProcessError):\n')
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
                                with open(f'{WORKING_FOLDER}/results/{TEST_NAME}/results/{system}_stocks_kn{query}_{win_length}_{test}.query' + '_except.txt', 'a') as tf:
                                    tf.write('query error:\n')
                                    tf.write(str(err))
                                    break
            print(f'Finished running {system}.')
        print(f'Finished running {test} test...')
    print('Finished Running systems.')



def run_wayeb(win_length, query, memorytest, timeout, max_events):
    subprocess.run(['java', '-Xmx50G',
                    '-jar', f'{WORKING_FOLDER}/jars/wayeb.jar',
                    'compile',
                    f'--patterns:{WORKING_FOLDER}/results/{TEST_NAME}/wayeb/wayeb_stocks_kn{query}_{win_length}.sre',
                    f'--fsmModel:{FSM_MODEL}',
                    f'--outputFsm:{WORKING_FOLDER}/results/{TEST_NAME}/wayeb/wayeb_stocks_kn{query}_{win_length}.fsm'],
                    timeout=timeout * 10, capture_output=False, check=True)
    return subprocess.run(['java', '-Xmx50G',
                           '-jar', f'{WORKING_FOLDER}/jars/wayeb.jar',
                           'recognition',
                           f'--fsm:{WORKING_FOLDER}/results/{TEST_NAME}/wayeb/wayeb_stocks_kn{query}_{win_length}.fsm',
                           f'--fsmModel:{FSM_MODEL}',
                           f'--stream:{WORKING_FOLDER}/stockstream/stocks.stream',
                           '--domainSpecificStream:stock',
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
                           'stock',
                           f'{WORKING_FOLDER}/results/{TEST_NAME}/esper/esper_stocks_kn{query}_{win_length}.query',
                           f'{WORKING_FOLDER}/stockstream/stocks.stream',
                           f'{memorytest}', f'{True}', f'{max_events}', f'{timeout}', f'{PRINT}', f'{POSTPROCESS}', f'{LIMIT}'],
                          timeout=timeout * 10, capture_output=True, check=True)

def main():
    print(f'Starting test with TEST_NAME {TEST_NAME}')
    create_folder()
    create_queries()
    run_systems()


if __name__ == "__main__":
    main()
