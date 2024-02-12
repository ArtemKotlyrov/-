import RPi.GPIO as IO
import time
from functools import reduce
import multiprocessing as mps
import traj

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
    except Exception as err:
        IO.output(s1, 0)
        IO.output(s2, 0)
        IO.output(e, 0)
        raise err
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
    except Exception as err:
        IO.output(s1, 0)
        IO.output(s2, 0)
        IO.output(e, 0)
        raise err
    IO.output(e, 0)

def H(steps, freq=100):
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
    except Exception as err:
        IO.output(s1, 0)
        IO.output(s2, 0)
        IO.output(e, 0)
        raise err
    IO.output(e, 0)

def W(steps, freq=100):
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
    except Exception as err:
        IO.output(s1, 0)
        IO.output(s2, 0)
        IO.output(e, 0)
        raise err
    IO.output(e, 0)

def Calibrate():
    while IO.input(sensorH):
        H(10)
    H(-10)
    while IO.input(sensorH):
        H(2)
    H(-50)
    while IO.input(sensorW):
        W(10)
    W(-10)
    while IO.input(sensorW):
        W(2)
    W(-50)

def Convert(line):
    to = {
        'а': 0b100000,
        'б': 0b110000,
        'в': 0b010111,
        'г': 0b110110,
        'д': 0b100110,
        'е': 0b100010,
        'ё': 0b100001,
        'ж': 0b010110,
        'з': 0b101011,
        'и': 0b010100,
        'й': 0b111101,
        'к': 0b101000,
        'л': 0b111000,
        'м': 0b101100,
        'н': 0b101110,
        'о': 0b101010,
        'п': 0b111100,
        'р': 0b111010,
        'с': 0b011100,
        'т': 0b011110,
        'у': 0b101001,
        'ф': 0b110100,
        'х': 0b110010,
        'ц': 0b100100,
        'ч': 0b111110,
        'ш': 0b100011,
        'щ': 0b101101,
        'ъ': 0b111011,
        'ы': 0b011101,
        'ь': 0b011111,
        'э': 0b010101,
        'ю': 0b110011,
        'я': 0b110101,
        '.': 0b010011,
        '!': 0b011010,
        '-': 0b001001,
        '«': 0b011001,
        '»': 0b001011,
        '(': 0b110001,
        ')': 0b001110,
        ',': 0b010000,
        '?': 0b010001
    }
    return reduce(lambda st, f_t: st.replace(*f_t))

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
    with sd.RawInputStream(samplerate=int(device_info["default_samplerate"]),
                           blocksize = 8000, device=device,
                           dtype="int16", channels=1, callback=callback):

        rec = KaldiRecognizer(model, int(device_info["default_samplerate"]))
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                res = rec.Result()
                print(res)
                if res: res_queue.put_nowait(res.item)
            else:
                print(rec.PartialResult())

text_queue = mps.Queue(10)
mps.Process(target=voice_main, name='voice_main', kwargs={
    'res_queue': text_queue,
    'device': None,
    'model': './vosk-models/custome-model-v1',
}, daemon=True)
LINE = 0
POS = 0


if __name__ == '__main__':
    Calibrate()
    while True:
        if text_queue.get() == 'печать':
            line = text_queue.get()
            traj.Print(line)
