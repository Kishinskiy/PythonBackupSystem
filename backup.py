import argparse
import datetime
import logging
import os
import sys
import zipfile
import shutil

# # MAX = 500*1024*1024    # 500Mb    - max chapter size
MAX = 500 * 1024 * 1024
BUF = 50 * 1024 * 1024 * 1024  # 50GB     - memory buffer size

# '''Loging options'''
current_data = str(datetime.date.today())
logging.basicConfig(
    format='%(asctime)s, %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    filename=current_data + '_backup.log',
    filemode='a',
    level=logging.DEBUG
)

# get arguments
def parse_input():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', nargs='*', type=str, required=True, help='Path to Source folder')
    parser.add_argument('--dest', nargs='*', type=str, required=True, help='Path to Destination folder')
    parser.add_argument('--name', nargs='*', type=str, required=True, help='Archive name .zip')
    parser.add_argument('--exclude', nargs='*', type=str, required=False, help='Exclude files txt ini doc etc')
    # parser.add_argument('-s', nargs='?', const=1, type=int, default=500)
    # parser.add_argument('-b', nargs='?', const=1, type=int, default=50)
    # no input means show me the help
    if len(sys.argv) == 0:
        parser.print_help()
        sys.exit()

    return parser.parse_args()


def file_split(FILE, MAX):
    """Split file into pieces, every size is  MAX = 15*1024*1024 Byte"""
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
    os.remove(FILE)
    print("Split archive to chapter complete")


# copy files and folder and compress into a zip file
def doprocess(source_folder, target_zip, excludes):
    zipf = zipfile.ZipFile(target_zip, "a")
    for subdir, dirs, files in os.walk(source_folder):
        for file in files:
            if file.split('.')[-1] not in excludes:
                try:
                    print(os.path.join(subdir, file))
                    logging.debug(os.path.join(subdir, file))
                    zipf.write(os.path.join(subdir, file))
                except Exception as e:
                    print(e)
                    logging.error(e, exc_info=False)

    try:
        logging.info("Archive created")
        print("Created ", target_zip)
    except Exception as e:
        print(e)
        logging.error(e, exc_info=False)


# copy files to a target folder
def docopy(source_folder, target_folder):
    if not os.path.exists(target_folder):
        os.mkdir(target_folder)
    for subdir, dirs, files in os.walk(source_folder):
        for file in files:
            print(os.path.join(subdir, file))
            # shutil.copy2(os.path.join(subdir, file), target_folder)
            try:
               # shutil.move(os.path.join(subdir, file), target_folder)
               shutil.copy2(os.path.join(subdir, file), target_folder)
            except IOError as e:
                print(e)
                logging.error(e, exc_info=False)



if __name__ == '__main__':
    try:
        logging.info('Backup is Started')
    except Exception as e:
        print(e)
    finally:
        print('Starting execution')

    arg = parse_input()
    dest = arg.dest[0]
    source = arg.source[0] # Получаем список src одним элементом
    sources = source.split(" ") #делим список на отдельные элементы разделяя их через пробел (Соотвтественно папки для копирования должны быть указанны через пробел
    name = arg.name[0]
    try:
        excludes = arg.exclude[0].split(" ")
    except Exception as e:
        print(e)

    path = 'Backup'
    if not os.path.exists(path):
        os.makedirs(path)
    retval = os.getcwd()
    os.chdir(path)

    for i in range(len(sources)):
        # compress to zip
        doprocess(sources[i], name, excludes) # Собираем все файлы в указанных каталогах в 1 архив

    file_split(name, MAX)  # Делим архив на части
    os.chdir(retval)
    docopy(path, dest)  # Копируем все части архива в папку назначения
    try:
        logging.info("Backup Finished")
    except Exception as e:
        print(e)
    finally:
        print('Ending execution')









