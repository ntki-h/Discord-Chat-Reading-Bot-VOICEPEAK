import discord
import os
from voice_synthesizer import VoiceSynthesizer

async def join_voice_channel(channel):
    await channel.connect()

async def leave_voice_channel(guild, bot=None):
    if guild.voice_client is not None:
        await guild.voice_client.disconnect()
        if bot is not None:
            bot.volume = 1.0
            bot.reset_emotion()

async def synthesize_and_play(message, voice_synthesizer, word_dictionary, ffmpeg_executable_path, volume=1.0):
    voice_client = message.guild.voice_client
    if voice_client and voice_client.is_connected() and message.author.voice:
        script = word_dictionary.convert_text(message.content)
        if len(script) > 140: # voicepeakが140文字以上の文字列を受け付けないため
            script = script[:140]
        output_path = f"{message.id}.wav"
        voice_synthesizer.synthesize(script, output_path=output_path)
        audio_source = discord.FFmpegPCMAudio(executable=ffmpeg_executable_path, source=output_path)
        volume_adjusted_source = discord.PCMVolumeTransformer(audio_source, volume=volume)
        voice_client.play(volume_adjusted_source, after=lambda e: os.remove(output_path))
