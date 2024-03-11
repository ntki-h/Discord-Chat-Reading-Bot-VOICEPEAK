import discord
from config import load_config
from voice_synthesizer import VoiceSynthesizer
from word_dictionary import WordDictionary
import events
import logging

# チャットデータを一時的に保持しておくためのクラス
class ChatData:
    def __init__(self, message, emotion_happy, emotion_sad, emotion_angry, emotion_fun):
        self.message = message
        self.emotion_happy = emotion_happy
        self.emotion_sad = emotion_sad
        self.emotion_angry = emotion_angry
        self.emotion_fun = emotion_fun
        
    def get_message(self):
        return self.message
    
    def get_emotion_happy(self):
        return self.emotion_happy
    
    def get_emotion_sad(self):
        return self.emotion_sad
    
    def get_emotion_angry(self):
        return self.emotion_angry
    
    def get_emotion_fun(self):
        return self.emotion_fun

class MyDiscordBot(discord.Client):
    def __init__(self, config, intents):
        super().__init__(intents=intents)
        self.config = config
        self.voice_synthesizer = VoiceSynthesizer(config["voicepeak_executable_path"], config["default_navigator"])
        self.word_dictionary = WordDictionary()
        self.prefix = config["prefix"]
        self.target_channel_id = None
        self.volume = 1.0
        self.emotion_happy = 100
        self.emotion_sad = 0
        self.emotion_angry = 0
        self.emotion_fun = 0
        self.logger = logging.getLogger(__name__)
        handler = logging.FileHandler('bot.log')
        handler.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.chat_data_list = []
        self.is_working = False

    def reset_emotion(self):
        self.emotion_happy = 100
        self.emotion_sad = 0
        self.emotion_angry = 0
        self.emotion_fun = 0
        self.voice_synthesizer.set_emotion(self.emotion_happy, self.emotion_sad, self.emotion_angry, self.emotion_fun)
        self.voice_synthesizer.set_pitch(0)

    async def on_ready(self):
        self.voice_synthesizer.set_emotion(self.emotion_happy, self.emotion_sad, self.emotion_angry, self.emotion_fun)
        print(f'{self.user} がログインしました')

    async def on_message(self, message):
        if message.author.bot:
            return

        try:
            if message.content.startswith(self.prefix + 'join'):
                if message.author.voice and message.author.voice.channel:
                    self.target_channel_id = message.channel.id
                    await events.join_voice_channel(message.author.voice.channel)
                else:
                    await message.channel.send("ボイスチャンネルに接続してください。")
            elif message.content.startswith(self.prefix + 'leave'):
                self.target_channel_id = None
                await events.leave_voice_channel(message.guild, self)
            elif message.content.startswith(self.prefix + 'volume'):
                try:
                    if self.is_valid_channel(message):
                        return
                    
                    new_volume = float(message.content.split(' ')[1])
                    self.volume = max(0.0, min(1.0, new_volume))
                    await message.channel.send(f"音量を{self.volume}に設定しました。")
                except (IndexError, ValueError):
                    await message.channel.send("正しい音量を指定してください。例: `" + self.prefix + "volume 0.5`")
            elif message.content.startswith(self.prefix + 'emotion'):
                try:
                    if self.is_valid_channel(message):
                        return
                    
                    args = message.content.split(' ')[1:]
                    self.emotion_happy = int(args[0])
                    self.emotion_sad = int(args[1])
                    self.emotion_angry = int(args[2])
                    self.emotion_fun = int(args[3])
                    self.voice_synthesizer.set_emotion(self.emotion_happy, self.emotion_sad, self.emotion_angry, self.emotion_fun)
                    await message.channel.send(f"感情を設定しました。happy={self.emotion_happy}, sad={self.emotion_sad}, angry={self.emotion_angry}, fun={self.emotion_fun}")
                except (IndexError, ValueError):
                    await message.channel.send("正しい感情を指定してください。例: `" + self.prefix + "emotion 100[幸せ] 0[悲しみ] 0[楽しみ] 0[怒り]`")
            elif message.content.startswith(self.prefix + 'pitch'):
                # 設定可能範囲は-300 ～ 300
                try:
                    if self.is_valid_channel(message):
                        return
                    
                    new_pitch = int(message.content.split(' ')[1])
                    self.pitch = max(-300, min(300, new_pitch))
                    self.voice_synthesizer.set_pitch(self.pitch)
                    await message.channel.send(f"音程を{self.pitch}に設定しました。")
                except (IndexError, ValueError):
                    await message.channel.send("正しい音程を指定してください。例: `" + self.prefix + "pitch 50`")
            elif message.content.startswith(self.prefix + 'dictionary'):
                try:
                    if self.is_valid_channel(message):
                        return
                    
                    _, original_word, converted_word = message.content.split(' ', 2)
                    self.word_dictionary.register_word(original_word, converted_word)
                    await message.channel.send(f"'{original_word}'を'{converted_word}'として登録しました。")
                except ValueError:
                    await message.channel.send("正しい形式で単語を指定してください。例: `" + self.prefix + "dictionary 元の単語 変換後の単語`")
            elif message.content.startswith(self.prefix + 'help'):
                help_message =  f"**ボットの使い方**\n" \
                                f"> {self.prefix}join: ボイスチャンネルに接続します。\n" \
                                f"> {self.prefix}leave: ボイスチャンネルから切断します。\n" \
                                f"> {self.prefix}volume: 音量を設定します。\n> \t例: `{self.prefix}volume 0.5`\n" \
                                f"> {self.prefix}emotion: 感情を設定します。\n> \t例: `{self.prefix}emotion 100[幸せ] 0[悲しみ] 0[怒り] 0[楽しみ]`\n" \
                                f"> {self.prefix}dictionary: 単語の辞書登録を行います。\n> \t例: `{self.prefix}dictionary 単語 読み方`\n"
                await message.channel.send(help_message)
            else:
                if self.is_valid_channel(message):
                    return
                
                # チャットデータを一時的に保持
                #self.chat_data_list.append(ChatData(message.content, self.emotion_happy, self.emotion_sad, self.emotion_angry, self.emotion_fun))
                
                await events.synthesize_and_play(message, self.voice_synthesizer, self.word_dictionary, self.config["ffmpeg_executable_path"], self.volume)
        except Exception as e:
            self.logger.error(f"Failed to process message: {e}")
            raise

    async def on_voice_state_update(self, member, before, after):
        try:
            # メンバーがボイスチャンネルから退出したかどうかを確認
            if before.channel and not after.channel:
                # ボットが接続しているボイスクライアントがあるかどうかを確認
                if before.channel.guild.voice_client:
                    # ボットを除いた後のチャンネル内のメンバーのリストを取得
                    members = [member for member in before.channel.members if member != self.user]
                    # ボット以外にメンバーがいなくなったことを確認
                    if len(members) == 0:
                        self.target_channel_id = None
                        await events.leave_voice_channel(before.channel.guild, self)
        except Exception as e:
            self.logger.error(f"Failed to update voice state: {e}")
            raise

    def is_valid_channel(self, message):
        if self.target_channel_id and message.channel.id != self.target_channel_id:
            return True
        if not message.guild.voice_client or not message.guild.voice_client.is_connected():
            return True
        
        return False

config = load_config()
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = MyDiscordBot(config, intents)
bot.run(config["discord_token"])
