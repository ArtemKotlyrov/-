import RPi.GPIO as IO
import time
from functools import reduce
import multiprocessing as mps
import traj
import sys

s1, d1, s2, d2, e = 1, 7, 8, 25, 12
b = [2, 3, 4, 17, 27, 22]
b = [2, 3, 4, 22, 17, 27]
sensorW = 24
sensorH = 23

IO.setmode(IO.BCM)
IO.setup((s1, s2, d1, d2, e), IO.OUT)
IO.setup(b, IO.OUT)
IO.setup((sensorH, sensorW), IO.IN, pull_up_down=IO.PUD_UP)

def A(steps, freq=100):
    T = 0.5/freq
    if steps>0:
        IO.output(d1, 0)
    else:
        IO.output(d1, 1)
    try:
        IO.output(e, 1)
        for i in range(abs(steps)):
            IO.output(s1, 1)
            time.sleep(T)
            IO.output(s1, 0)
            time.sleep(T)
    finally:
        IO.output(s1, 0)
        IO.output(s2, 0)
        IO.output(e, 0)

def B(steps, freq=100):
    T = 0.5/freq
    if steps>0:
        IO.output(d2, 0)
    else:
        IO.output(d2, 1)
    try:
        IO.output(e, 1)
        for i in range(abs(steps)):
            IO.output(s2, 1)
            time.sleep(T)
            IO.output(s2, 0)
            time.sleep(T)
    finally:
        IO.output(s1, 0)
        IO.output(s2, 0)
        IO.output(e, 0)

def H(steps, freq=100, e_end=0):
    T = 0.5/freq
    if steps>0:
        IO.output(d1, 0)
        IO.output(d2, 0)
    else:
        IO.output(d1, 1)
        IO.output(d2, 1)
    try:
        IO.output(e, 1)
        for i in range(abs(steps)):
            IO.output(s2, 1)
            IO.output(s1, 1)
            time.sleep(T)
            IO.output(s2, 0)
            IO.output(s1, 0)
            time.sleep(T)
    finally:
        IO.output(s1, 0)
        IO.output(s2, 0)
        IO.output(e, e_end)

def W(steps, freq=100, e_end=0):
    T = 0.5/freq
    if steps>0:
        IO.output(d1, 1)
        IO.output(d2, 0)
    else:
        IO.output(d1, 0)
        IO.output(d2, 1)
    try:
        IO.output(e, 1)
        for i in range(abs(steps)):
            IO.output(s2, 1)
            IO.output(s1, 1)
            time.sleep(T)
            IO.output(s2, 0)
            IO.output(s1, 0)
            time.sleep(T)
    finally:
        IO.output(s1, 0)
        IO.output(s2, 0)
        IO.output(e, e_end)

def Calibrate():
    try:
        IO.output(e, 1)
        IO.output(d1, 0)
        IO.output(d2, 0)
        while IO.input(sensorH):
            IO.output(s2, 1)
            IO.output(s1, 1)
            time.sleep(1/200)
            IO.output(s2, 0)
            IO.output(s1, 0)
            time.sleep(1/200)

        IO.output(d1, 1)
        IO.output(d2, 1)
        for i in range(90):
            IO.output(s2, 1)
            IO.output(s1, 1)
            time.sleep(1/200)
            IO.output(s2, 0)
            IO.output(s1, 0)
            time.sleep(1/200)

        IO.output(d1, 1)
        IO.output(d2, 0)
        while IO.input(sensorW):
            IO.output(s2, 1)
            IO.output(s1, 1)
            time.sleep(1/200)
            IO.output(s2, 0)
            IO.output(s1, 0)
            time.sleep(1/200)

        IO.output(d1, 0)
        IO.output(d2, 1)
        for i in range(1020):
            IO.output(s2, 1)
            IO.output(s1, 1)
            time.sleep(1/200)
            IO.output(s2, 0)
            IO.output(s1, 0)
            time.sleep(1/200)
    finally:
        IO.output(e, 0)
        IO.output(s2, 0)
        IO.output(s1, 0)

to = {
    'а': [1,0,0,0,0,0],
    'б': [1,1,0,0,0,0],
    'в': [0,1,0,1,1,1],
    'г': [1,1,0,1,1,0],
    'д': [1,0,0,1,1,0],
    'е': [1,0,0,0,1,0],
    'ё': [1,0,0,0,0,1],
    'ж': [0,1,0,1,1,0],
    'з': [1,0,1,0,1,1],
    'и': [0,1,0,1,0,0],
    'й': [1,1,1,1,0,1],
    'к': [1,0,1,0,0,0],
    'л': [1,1,1,0,0,0],
    'м': [1,0,1,1,0,0],
    'н': [1,0,1,1,1,0],
    'о': [1,0,1,0,1,0],
    'п': [1,1,1,1,0,0],
    'р': [1,1,1,0,1,0],
    'с': [0,1,1,1,0,0],
    'т': [0,1,1,1,1,0],
    'у': [1,0,1,0,0,1],
    'ф': [1,1,0,1,0,0],
    'х': [1,1,0,0,1,0],
    'ц': [1,0,0,1,0,0],
    'ч': [1,1,1,1,1,0],
    'ш': [1,0,0,0,1,1],
    'щ': [1,0,1,1,0,1],
    'ъ': [1,1,1,0,1,1],
    'ы': [0,1,1,1,0,1],
    'ь': [0,1,1,1,1,1],
    'э': [0,1,0,1,0,1],
    'ю': [1,1,0,0,1,1],
    'я': [1,1,0,1,0,1],
    '.': [0,1,0,0,1,1],
    '!': [0,1,1,0,1,0],
    '-': [0,0,1,0,0,1],
    '«': [0,1,1,0,0,1],
    '»': [0,0,1,0,1,1],
    '(': [1,1,0,0,0,1],
    ')': [0,0,1,1,1,0],
    ',': [0,1,0,0,0,0],
    '?': [0,1,0,0,0,1],
}

def voice_main(res_queue: mps.Queue, device: str, model: str):
    import queue
    import sounddevice as sd
    import sys
    from vosk import Model, KaldiRecognizer
    q = queue.Queue()
    def callback(indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        q.put(bytes(indata))
    device_info = sd.query_devices(device, "input")
    model = Model(model_path=model)
    with sd.RawInputStream(samplerate=int(device_info["default_samplerate"]),
                           blocksize = 8000, device=device,
                           dtype="int16", channels=1, callback=callback):

        rec = KaldiRecognizer(model, int(device_info["default_samplerate"]))
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                res = rec.Result()
                print(res)
                if res: 
                    res = eval(res)["text"]
                    if res:
                        res_queue.put_nowait(res)
            else:
                print(rec.PartialResult())

def Beat(letter):
    for i in range(3):
        for id, pin in zip(letter, b):
            if id==0:
                continue
            if pin in [b[2-1], b[5-1]]:
                IO.output(pin, 1)
                time.sleep(0.15)
                IO.output(pin, 0)
                time.sleep(0.2)
            IO.output(pin, 1)
            time.sleep(0.15)
            IO.output(pin, 0)
        if sum(letter) == 1:
            time.sleep(0.2)

def Print(line):
    cities, recalc, char = traj.PrepareText(line, 28)
    res = traj.simulated_annealing(cities)[0]
    path = traj.GetPathFromRes(res, recalc, char)
    try:
        Beat(to[path[0][1]])
        X, Y = 0, 0
        for pos, ch in path[1:]:
            W(pos[0]-X, 200, 1)
            H(pos[1]-Y, 200, 1)
            X, Y = pos
            if ch:
                Beat(to[ch])
    finally:
        IO.output(e, 0)
        IO.output(b, 0)

LINE = 0
POS = 0



if __name__ == '__main__':
    Print("однажды")
    exit()
    text_queue = mps.Queue(10)
    rec = mps.Process(target=voice_main, name='voice_main', kwargs={
        'res_queue': text_queue,
        'device': None,
        'model': './vosk-models/custome-model-v1',
    }, daemon=True)
    rec.start()
    # Calibrate()
    while True:
        cmd = text_queue.get()
        if cmd == 'печать':
            line = text_queue.get()
            Print(line)
        elif cmd in ('новый лист', 'калибровка'):
            Calibrate()
        elif cmd == 'стоп':
            break
        elif cmd in ('строка вверх', 'вверх', 'символ вверх'):
            H(round(10/0.155))
        elif cmd in ('строка вниз', 'вниз', 'символ вниз'):
            H(round(-10/0.155))
        elif cmd in ('символ вправо', 'вправо'):
            W(round(6/0.155))
        elif cmd in ('символ влево', 'влево'):
            W(round(-6/0.155))


