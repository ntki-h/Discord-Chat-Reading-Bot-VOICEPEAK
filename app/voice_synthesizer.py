import logging
import subprocess
import os

class VoiceSynthesizer:
    def __init__(self, voicepeak_path, narrator):
        self.voicepeak_path = voicepeak_path
        self.narrator = narrator
        self.logger = logging.getLogger(__name__)
        handler = logging.FileHandler('voice_synthesizer.log')
        handler.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.pitch = 0

    def set_emotion(self, happy, sad, angry, fun):
        self.emotion_happy = happy
        self.emotion_sad = sad
        self.emotion_angry = angry
        self.emotion_fun = fun

    def set_pitch(self, pitch):
        self.pitch = pitch

    def synthesize(self, script, output_path="output.wav"):
        args = [
            self.voicepeak_path,
            "-s", script,
            "-n", self.narrator,
            "-o", output_path,
            "-e", f"happy={self.emotion_happy},sad={self.emotion_sad},angry={self.emotion_angry},fun={self.emotion_fun}"
            "--pitch", self.pitch
        ]
        try:
            subprocess.run(args, check=True)
        except subprocess.CalledProcessError as e:
            stderr_output = e.stderr.decode('utf-8') if e.stderr else 'No stderr output'
            error_message = f"Voicepeak failed with error code {e.returncode}: {stderr_output}"
            self.logger.error(error_message)  # エラーメッセージをログに出力
            raise RuntimeError(error_message) from e
        if not os.path.exists(output_path):
            error_message = f"Expected audio file not found: {output_path}"
            self.logger.error(error_message)  # エラーメッセージをログに出力
            raise FileNotFoundError(error_message)
        return output_path