import subprocess
import os

class VoiceSynthesizer:
    def __init__(self, voicepeak_path, narrator):
        self.voicepeak_path = voicepeak_path
        self.narrator = narrator
        
    def set_emotion(self, happy, sad, angry, fun):
        self.emotion_happy = happy
        self.emotion_sad = sad
        self.emotion_angry = angry
        self.emotion_fun = fun

    def synthesize(self, script, output_path="output.wav"):
        args = [
            self.voicepeak_path,
            "-s", script,
            "-n", self.narrator,
            "-o", output_path,
            "-e", f"happy={self.emotion_happy},sad={self.emotion_sad},angry={self.emotion_angry},fun={self.emotion_fun}"
        ]
        try:
            subprocess.run(args, check=True)
        except subprocess.CalledProcessError as e:
            stderr_output = e.stderr.decode('utf-8') if e.stderr else 'No stderr output'
            raise RuntimeError(f"Voicepeak failed with error code {e.returncode}: {stderr_output}") from e
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Expected audio file not found: {output_path}")
        return output_path
