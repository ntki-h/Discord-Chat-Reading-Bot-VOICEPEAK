import discord
from config import load_config
from voice_synthesizer import VoiceSynthesizer
from word_dictionary import WordDictionary
import events

class MyDiscordBot(discord.Client):
    def __init__(self, config, intents):
        super().__init__(intents=intents)
        self.config = config
        self.voice_synthesizer = VoiceSynthesizer(config["voicepeak_executable_path"], config["default_navigator"])
        self.word_dictionary = WordDictionary()
        self.prefix = config["prefix"]
        self.volume = 1.0
        self.emotion_happy = 100
        self.emotion_sad = 0
        self.emotion_angry = 0
        self.emotion_fun = 0
        
    def reset_emotion(self):
        self.emotion_happy = 100
        self.emotion_sad = 0
        self.emotion_angry = 0
        self.emotion_fun = 0
        self.voice_synthesizer.set_emotion(self.emotion_happy, self.emotion_sad, self.emotion_angry, self.emotion_fun)

    async def on_ready(self):
        self.voice_synthesizer.set_emotion(self.emotion_happy, self.emotion_sad, self.emotion_angry, self.emotion_fun)
        print(f'{self.user} がログインしました')

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.content.startswith(self.prefix + 'join'):
            if message.author.voice and message.author.voice.channel:
                await events.join_voice_channel(message.author.voice.channel)
            else:
                await message.channel.send("ボイスチャンネルに接続してください。")
        elif message.content.startswith(self.prefix + 'leave'):
            await events.leave_voice_channel(message.guild, self)
        elif message.content.startswith(self.prefix + 'volume'):
            try:
                new_volume = float(message.content.split(' ')[1])
                self.volume = max(0.0, min(1.0, new_volume))
                await message.channel.send(f"音量を{self.volume}に設定しました。")
            except (IndexError, ValueError):
                await message.channel.send("正しい音量を指定してください。例: `" + self.prefix + "volume 0.5`")
        elif message.content.startswith(self.prefix + 'emotion'):
            try:
                args = message.content.split(' ')[1:]
                self.emotion_happy = int(args[0])
                self.emotion_sad = int(args[1])
                self.emotion_angry = int(args[2])
                self.emotion_fun = int(args[3])
                self.voice_synthesizer.set_emotion(self.emotion_happy, self.emotion_sad, self.emotion_angry, self.emotion_fun)
                await message.channel.send(f"感情を設定しました。happy={self.emotion_happy}, sad={self.emotion_sad}, angry={self.emotion_angry}, fun={self.emotion_fun}")
            except (IndexError, ValueError):
                await message.channel.send("正しい感情を指定してください。例: `" + self.prefix + "emotion 100[幸せ] 0[悲しみ] 0[楽しみ] 0[怒り]`")
        elif message.content.startswith(self.prefix + 'dictionary'):
            try:
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
                            f"> {self.prefix}emotion: 感情を設定します。\n> \t例: `{self.prefix}emotion 100[幸せ] 0[悲しみ] 0[楽しみ] 0[怒り]`\n"
            await message.channel.send(help_message)
        else:
            await events.synthesize_and_play(message, self.voice_synthesizer, self.word_dictionary, self.config["ffmpeg_executable_path"], self.volume)

    async def on_voice_state_update(self, member, before, after):
        if before.channel and not after.channel:
            if before.channel.guild.voice_client:
                members = before.channel.members
                if len(members) == 1 and self.user in members:
                    await events.leave_voice_channel(before.channel.guild, self)

config = load_config()
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = MyDiscordBot(config, intents)
bot.run(config["discord_token"])
