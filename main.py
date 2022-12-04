import itertools
import sys
import time
from pathlib import Path
from subprocess import Popen
from threading import Thread


loop_path = 'C:/Users/User/Desktop/forex/new/loop7.m'

# User defined values
jj = 0
st = 460
fin2 = 517
stf = 10
finf = 10
low = .04
high = 1
gsfact1 = 0.9
dgs = 0.2
dcy = 50
dd = 20
dlr = 0
l2 = 0

cycles_st = 1100
cycles_fin = 900
cycles_delta = -50
days_st = 1
days_fin = 150
days_delta = 1
cells_st = 350
cells_fin = 240
cells_delta = -30
lrate_st = 8
lrate_fin = 5
lrate_delta = -1
gsfact_st = 7
gsfact_fin = 8
gsfact_delta = 1

n_gpus = 3


def run_matlab(script: str):
    pout = Popen(['matlab.exe', '-nosplash', '-nodesktop', '-r', f'\"{script}\"'])


def loop(jj, st, fin2, stf, finf, high, low, gsfact, dgs, cycles,
         dcy, day, dd, lrate, dlr, cells, l2, igpu):
    vars = f'jj={jj}; st={st}; fin2={fin2}; stf={stf}; finf={finf}; high={high}; low={low}; gsfact={gsfact};' \
           f'dgs={dgs}; dcy={dcy}; day={day}; dd={dd}; lrate={lrate}; dlr={dlr}; igpu={igpu}; cells={cells};' \
           f'l2={l2}; cycles={cycles}'
    loop = Path(loop_path)
    run_matlab(f'{vars};{str(loop)};')


def generate_combinations():
    cycles = [x for x in range(cycles_st, cycles_fin, cycles_delta)]
    days = [x for x in range(days_st, days_fin, days_delta)]
    cells = [x for x in range(cells_st, cells_fin, cells_delta)]
    lrates = [x * 0.001 for x in range(lrate_st, lrate_fin, lrate_delta)]
    gsfacts = [0.1 * x for x in range(gsfact_st, gsfact_fin, gsfact_delta)]

    result = list(itertools.product(cycles, days, cells, lrates, gsfacts))
    return result


def join_threads(threads: list):
    [thread.join() for thread in threads]


def chunks(l, n):
    """Yield n number of striped chunks from l."""
    for i in range(0, n):
        yield l[i::n]


def run_scripts(scripts_path: Path):
    sys.path.insert(1, str(scripts_path))

    threads = []
    chunkz = chunks(generate_combinations(), n_gpus)
    for idx, chunk in enumerate(chunkz):
        def worker(igpu: int):
            for cycles, day, cells, lrate, gsfact in chunk:
                loop(jj, st, fin2, stf, finf, high, low, gsfact, dgs, cycles,
                     dcy, day, dd, lrate, dlr, cells, l2, igpu)
                time.sleep(0.8)

        thread = Thread(target=worker, args=(idx + 1,))
        thread.start()
        threads.append(thread)

    return threads


def main():
    matlab_path = Path(r'C:\Users\sfous\Desktop\forex\nick\matlab_gpu_script')
    threads = run_scripts(scripts_path=matlab_path)
    #quit_all(engines=engines)
    join_threads(threads=threads)


if __name__ == '__main__':
    main()
