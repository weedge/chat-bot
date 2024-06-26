import os
import logging
import asyncio

import unittest

from src.common.interface import IDetector, IRecorder
from src.common.logger import Logger
from src.common.factory import EngineFactory, EngineClass
from src.common.session import Session
from src.common.utils import audio_utils
from src.common.types import SessionCtx, TEST_DIR, MODELS_DIR, RECORDS_DIR, INT16_MAX_ABS_VALUE
import src.modules.speech

r"""
python -m unittest test.modules.speech.recorder.test_record.TestRMSRecorder.test_record
python -m unittest test.modules.speech.recorder.test_record.TestRMSRecorder.test_multi_record
python -m unittest test.modules.speech.recorder.test_record.TestRMSRecorder.test_wakeword_rms_record

RECODER_TAG=wakeword_rms_recorder python -m unittest test.modules.speech.recorder.test_record.TestRMSRecorder.test_record
RECODER_TAG=wakeword_rms_recorder python -m unittest test.modules.speech.recorder.test_record.TestRMSRecorder.test_multi_record
RECODER_TAG=wakeword_rms_recorder python -m unittest test.modules.speech.recorder.test_record.TestRMSRecorder.test_wakeword_rms_record
"""


class TestRMSRecorder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tag = os.getenv('RECODER_TAG', "rms_recorder")
        cls.input_device_index = os.getenv('MIC_IDX', None)

        cls.detector_tag = os.getenv('DETECTOR_TAG', "porcupine_wakeword")
        cls.wake_words = os.getenv('WAKE_WORDS', "小黑")
        audio_file = os.path.join(
            RECORDS_DIR, f"tmp_wakeword_porcupine.wav")
        model_path = os.path.join(
            MODELS_DIR, "porcupine_params_zh.pv")
        keyword_paths = os.path.join(
            MODELS_DIR, "小黑_zh_mac_v3_0_0.ppn")
        cls.access_key = os.getenv('PORCUPINE_ACCESS_KEY', "")
        cls.audio_file = os.getenv('AUDIO_FILE', audio_file)
        cls.model_path = os.getenv('MODEL_PATH', model_path)
        cls.keyword_paths = os.getenv('KEYWORD_PATHS', keyword_paths)

        Logger.init(logging.DEBUG, is_file=False)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.kwargs = {}
        self.kwargs["input_device_index"] = None if self.input_device_index is None else int(
            self.input_device_index)
        self.recorder: IRecorder = EngineFactory.get_engine_by_tag(
            EngineClass, self.tag, **self.kwargs)
        self.session = Session(**SessionCtx(
            "test_client_id").__dict__)

    def tearDown(self):
        self.recorder and self.recorder.close()
        self.session.close()

    def test_record(self):
        frames = self.recorder.record_audio(self.session)
        self.assertGreater(len(frames), 0)
        data = b''.join(frames)
        file_path = asyncio.run(audio_utils.save_audio_to_file(
            data, os.path.join(RECORDS_DIR, "test.wav")))
        print(file_path)

    def test_multi_record(self):
        frames = self.recorder.record_audio(self.session)
        self.assertGreater(len(frames), 0)
        data = b''.join(frames)
        file_path = asyncio.run(audio_utils.save_audio_to_file(
            data, os.path.join(RECORDS_DIR, "test.wav")))
        print(file_path)

        self.recorder2 = EngineFactory.get_engine_by_tag(
            EngineClass, self.tag, **self.kwargs)
        frames = self.recorder2.record_audio(self.session)
        self.assertGreater(len(frames), 0)
        data = b''.join(frames)
        file_path = asyncio.run(audio_utils.save_audio_to_file(
            data, os.path.join(RECORDS_DIR, "test2.wav")))
        print(file_path)
        self.recorder2.close()

    def test_wakeword_rms_record(self):
        def on_wakeword_detected(session, data):
            print(
                f"bot_name:{session.ctx.state['bot_name']} wakeword detected")
        kwargs = {}
        kwargs["access_key"] = self.access_key
        kwargs["wake_words"] = self.wake_words
        kwargs["model_path"] = self.model_path
        # kwargs["on_wakeword_detected"] = on_wakeword_detected
        kwargs["keyword_paths"] = self.keyword_paths.split(',')
        self.session.ctx.waker = EngineFactory.get_engine_by_tag(
            EngineClass, self.detector_tag, **kwargs)
        self.session.ctx.waker.set_args(
            on_wakeword_detected=on_wakeword_detected)

        round = 1
        for i in range(round):
            frames = self.recorder.record_audio(self.session)
            self.assertGreaterEqual(len(frames), 0)
            data = b''.join(frames)
            file_path = asyncio.run(audio_utils.save_audio_to_file(
                data, os.path.join(RECORDS_DIR, f"test{i}.wav")))
            print(file_path)
