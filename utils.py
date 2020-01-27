import shutil
import os
import time
import re
import sys
import json
import requests
import vk
DATAPATH = 'DATA'
WAIT_TIME = 0.34
# Returns joined datapath
def dirpathgen(dirname):
    if not os.path.isdir(DATAPATH):
        os.mkdir(DATAPATH)
    return os.path.join(DATAPATH, dirname)

# Creates a new dirname dir and copies all assets here and returns dirname,
# if it can't create dir with given name, it creates new dir with different name and returns new dirname
def mklsdir(dirname):
    dirpath = dirpathgen(dirname)
    if os.path.isdir(dirpath):
        exit_with_error('Такая папка (%s) уже есть, но файл сохранения не найден. Удалите папку вручную.' % dirpath)

    os.mkdir(dirpath)
    shutil.copytree('css', os.path.join(dirpath,'css'))
    shutil.copytree('js', os.path.join(dirpath,'js'))
    shutil.copytree('fonts', os.path.join(dirpath,'fonts'))
    os.mkdir(os.path.join(dirpath,'messages'))

    return dirname

# Creates filename file in messages and returns this file for write
def getlsfile(dirname,filename):
    dirpath = dirpathgen(dirname)
    return open(os.path.join(dirpath,'messages',filename),'wb')

# Writes header to file
def writeheader(file):
    with open('header.html') as header:
        headercat = header.read().encode("UTF-8")
    file.write(headercat)

# Writes footer to file
def writefooter(file):
    with open('footer.html') as footer:
        footercat = footer.read().encode("UTF-8")
    file.write(footercat)

# Reads json from file with filename
def json_read(filename):
    with open(filename) as f:
        return json.load(f)

# Wait seconds seconds
def sleep(seconds):
    time.sleep(seconds)

# Returns time by unixformat
def gen_time(id):
    return time.strftime("%D %H:%M", time.localtime(id))

# Print a progress bar with progress% progress
def print_pb(progress):
    width = 30-2
    current_progress = int(progress*width)
    pb = '['
    pb += current_progress * '#'
    pb += (width-current_progress) * '-'
    pb += '] '
    pb += str(int(progress*100)) + '%'
    print(pb, end = '\r')

def to_json(object):
    return json.dumps(object, ensure_ascii=False)

def redo(func):
    def redo_func(*args,**kwargs):
        try:
            return func(*args,**kwargs)
        except requests.exceptions.ReadTimeout:
            warning("ReadTimeout: вторая попытка через 5 секунд")
            sleep(5)
            return func(*args,**kwargs)
        except vk.exceptions.VkAPIError:
            warning("VK api error: вторая попытка через 5 секунд")
            sleep(5)
            return func(*args,**kwargs)
    return redo_func

def done_read(me):
    uid = me['uid']
    if os.path.isfile('%dsave.json'%uid):
        return json_read('%dsave.json'%uid)
    else:
        return {"chat":[],"private":[], "filename":'%dsave.json'%uid,'uid':-1}

def done_write(obj):
    with open('%dsave.json'%obj['uid'],'w') as done:
        done.write(to_json(obj))

def done_remove(obj):
    os.remove('%dsave.json'%obj['uid'])

def exit_with_error(error):
    print("[ERROR] {}".format(error))
    sys.exit(1)

def info(*text):
    print("[INFO] {}".format(" ".join(text)))

def warning(*text):
    print("[WARNING] {}".format(" ".join(text)))

def transliterate(text):
    symbols = ("абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
        "abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA")
    tr = { ord(a):ord(b) for a, b in zip(*symbols) }
    return text.translate(tr)