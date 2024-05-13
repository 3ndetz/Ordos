# EXAMPLE FILE! USE YOURS STT CLASS
# ПРИМЕР ИНТЕРФЕЙСА для связи с Docker
# ИНТЕРФЕЙС ДЛЯ РАСПОЗНАВАНИЯ РЕЧИ МОЖЕТЕ ВСТАВИТЬ САМИ см. код. Может кстати будет в другом репозитории у меня в гите


from multiprocessing import Process
import time
from datetime import datetime


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def calcTime(time):
    return bcolors.OKGREEN + str((datetime.now() - time).total_seconds()) + bcolors.ENDC


import multiprocessing
from multiprocessing.managers import SyncManager


class MyManager(SyncManager):
    pass


# control dict
syncdict = {}

# llm

# sttCtx = multiprocessing.N

# tts
tts_inputQueue = multiprocessing.Queue()
tts_outputQueue = multiprocessing.Queue()


def get_tts_input_q():
    return tts_inputQueue


def get_tts_output_q():
    return tts_outputQueue


def get_dict():
    return syncdict


def nemo_tts_process(manager):
    debug_iter = 0
    # import your STT class/interface with method audio_transcribe
    from STT.stream_stt_inf import NemoSpeechTranscriber  # my stt class USE YOURS
    transcriber = NemoSpeechTranscriber()
    transcriber.check_initialization()
    while True:
        inp = manager.tts_input_q().get()
        print("INPUT GOT!", debug_iter)  # ,inp,debug_iter)
        debug_iter += 1
        # inp = inp+" "+str(debug_iter)
        output = transcriber.audio_transcribe(audio_samples=inp["bytes_io"], audio_settings=inp["audio_settings"])
        print("PROCESSING READY, SENDING OUT! ", inp)
        manager.tts_output_q().put(output)
        # print('waiting for action, syncdict %s' % (syncdict))
        # time.sleep(5)


if __name__ == "__main__":

    MyManager.register("syncdict", get_dict)
    MyManager.register("tts_input_q", get_tts_input_q)
    MyManager.register("tts_output_q", get_tts_output_q)

    manager = MyManager(("0.0.0.0", 6006), authkey=b"YOUR SECURE KEY ПРИДУМАЙТЕ only eng symbols")

    print("Started listener manager 0.0.0.0 : 6006")
    manager.start()
    STT_Process = Process(
        target=nemo_tts_process,
        args=(manager,))
    STT_Process.start()
    while True:
        time.sleep(1)
        if manager.syncdict().get("stop", False) == True:
            print('TERMINATING DOCKER RECIEVER')
            break
    STT_Process.terminate()
    STT_Process.join()
    manager.shutdown()
