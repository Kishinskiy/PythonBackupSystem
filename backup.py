##
# Script to copy files and compress them and put them in a separate location
# Amit Sengupta, Sep 2015, HYD
# Written in Python 2.7
###
import argparse
import os
import sys
import zipfile
import shutil


# # MAX = 500*1024*1024    # 500Mb    - max chapter size
MAX = 500*1024*1024
BUF = 50*1024*1024*1024    # 50GB     - memory buffer size


# get arguments
def parse_input():
    parser = argparse.ArgumentParser()
    parser.add_argument('-src', nargs='*', type=str, required=True, help='Path to Source folder')
    parser.add_argument('-dst', nargs='*', type=str, required=True, help='Path to Destination folder')
    parser.add_argument('-name', nargs='*', type=str, required=True, help='Archive name .zip')
    # parser.add_argument('-s', nargs='?', const=1, type=int, default=500)
    # parser.add_argument('-b', nargs='?', const=1, type=int, default=50)
    # no input means show me the help
    if len(sys.argv) == 0:
        parser.print_help()
        sys.exit()

    return parser.parse_args()


def file_split(FILE, MAX):
    '''Split file into pieces, every size is  MAX = 15*1024*1024 Byte'''
    chapters = 1
    uglybuf = ''



    with open(FILE, 'rb') as src:
        while True:
            tgt = open(FILE + '.%03d' % chapters, 'wb')
            written = 0
            while written < MAX:
                if len(uglybuf) > 0:
                    tgt.write(uglybuf)
                tgt.write(src.read(min(BUF, MAX - written)))
                written += min(BUF, MAX - written)
                uglybuf = src.read(1)
                if len(uglybuf) == 0:
                    break
            tgt.close()
            if len(uglybuf) == 0:
                break
            chapters += 1
    print("Split archive to chapter complete")


# copy files and folder and compress into a zip file
def doprocess(source_folder, target_zip):
    zipf = zipfile.ZipFile(target_zip, "w")
    for subdir, dirs, files in os.walk(source_folder):
        for file in files:
            print(os.path.join(subdir, file))
            zipf.write(os.path.join(subdir, file))

    print("Created ", target_zip)


# copy files to a target folder
def docopy(source_folder, target_folder):
    for subdir, dirs, files in os.walk(source_folder):
        for file in files:
            print(os.path.join(subdir, file))
            # shutil.copy2(os.path.join(subdir, file), target_folder)
            shutil.move(os.path.join(subdir, file), target_folder)


if __name__ == '__main__':
    print('Starting execution')

    arg = parse_input()
    dest = arg.dst[0]
    source = arg.src[0]
    name = arg.name[0]
    # size = arg.s[0]
    # buf = arg.b[0]
    #
    # MAX = size * 1024 * 1024
    # BUF = buf * 1024 * 1024 * 1024

    path = 'Backup'
    if not os.path.exists(path):
        os.makedirs(path)

    os.chdir(path)

    # compress to zip
    doprocess(source, name)

    # split zip archive
    file_split(name, MAX)

    os.remove(name)

    os.chdir("..")

    if not os.path.exists(dest):
        os.makedirs(dest)


    # copy to backup folder
    docopy(path, dest)

    print('Ending execution')
