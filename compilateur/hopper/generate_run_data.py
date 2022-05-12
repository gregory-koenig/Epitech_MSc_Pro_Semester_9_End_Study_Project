from time import process_time
import time
import argparse
import sys
import os
import subprocess
import json

def main():

    arguments = get_arguments()

    run_executables(arguments.nbexec)

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-nb", "--nbexec", nargs='?',  const=10, default=10, type=int, help="set the number of executions (10 by default)")

    args = parser.parse_args()

    return args

# subprocess is separate from another. We need to go in /build each time
def run_executables(nbexec):
    data = {}
    timestr = time.strftime("%d:%m:%Y-%H:%M:%S")

    for file in os.listdir('build'):
        exec_name = file
        data[exec_name] = []

        print(f"run {file} {str(nbexec)} times")
        command = f"cd build; ./{file}"
        t1_all_exec_start = process_time()

        for i in range(nbexec):
            print(file, "execution n°", i + 1)
            t1_start = process_time() 
            subprocess.run(command,  shell=True)
            t1_stop = process_time()

            if i == 0:
                min = t1_stop-t1_start
                max = t1_stop-t1_start
                avg = 0

            if t1_stop-t1_start > max:
                max = t1_stop-t1_start
            if t1_stop-t1_start < min:
                min = t1_stop-t1_start

            avg += t1_stop-t1_start

        t1_all_exec_stop = process_time()

        # Multiply by 1000 to get time in ms and round to 2 decimals
        avg /= nbexec
        avg *= 1000
        avg = round(avg, 2)
        min *= 1000
        min = round(min, 2)
        max *= 1000
        max = round(max, 2)
        
        # print(f"Elapsed time during the {str(nbexec)} executions in seconds:", t1_all_exec_stop-t1_all_exec_start) 
        print(file, "temps d'exécutions")
        print("min :", min)
        print("max :", max)
        print("average :", avg)
        data[exec_name].append({'timeStamp': timestr, 'min': min, "max": max, "avg": avg})

    print(data)
    with open('data.txt', 'w') as outfile:
        json.dump(data, outfile)

    return 0

if __name__ == "__main__":
    sys.exit(main())
