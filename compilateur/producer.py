from posixpath import split
import time
import json
from kafka import KafkaProducer
import argparse
import os
import sys

# Manage programs arguments
parser = argparse.ArgumentParser(description='Compiler9000 kafka producer')
parser.add_argument('--file', help='You need to pass file path like that -> FOLDERNAME/FILENAMEWITHEXTENTION \n EXEMPLE : --file folder/test.json')
parser.add_argument('--folder', help='You need to pass a folder like that -> FOLDERNAME/')

parser.add_argument('--host', nargs='?', help='Hostname')
parser.add_argument('--port', nargs='?', help='Port')

hostname = 'localhost'
port = 9092

args = parser.parse_args()

# overwrite port and hostname if passed in args
if args.host != None:
    hostname = args.host

if args.port != None:
    port = args.port

# check arguments validity
if args.file == None and args.folder == None:
    print('Needed a file or directory check --help')
    sys.exit(0)

if args.file != None:
    if '#' in args.file:
        print('File already sended please select an unknowed file')
        sys.exit(0)

    elif '.json' not in args.file:
        print('file need to be JSON')
        sys.exit(0)
    
    elif os.path.isfile(args.file) == False:
        print(f'{args.file} is not a valid File (verify you target an existing file or check the path of the file)')
        sys.exit(0)

if args.folder != None:
    if '/' != args.folder[-1]:
        print('Need to have / at last char')
        sys.exit(0)

    elif os.path.isdir(args.folder) == False:
        print('You need to give a real folder or check folder path. You can look help if needed')
        sys.exit(0)

file_list = []

if args.file != None:
    file_list.append(args.file)

elif args.folder != None:
    tmp = os.listdir(args.folder)

    for i in range(len(tmp)):
        if '#' not in tmp[i]:
            file_list.append(f'{args.folder}{tmp[i]}')

# kafka producer connection
producer = KafkaProducer(bootstrap_servers=[f'{hostname}:{port}'], value_serializer=lambda x: json.dumps(x).encode('utf-8'))

for file in file_list:
    file_content = ''

    # read file content
    with open(file, 'r') as f:
        file_content = f.read()
        f.close()

    # send to kafka server
    producer.send('files', value={'filename': file.split('/')[-1], 'file': file_content})
    time.sleep(1)

    # rename file once readed and sended it
    splited_path = file.split('/')
    new_path = '/#'.join(['/'.join(splited_path[:-1]), splited_path[-1:][0]])

    os.rename(file, new_path)
