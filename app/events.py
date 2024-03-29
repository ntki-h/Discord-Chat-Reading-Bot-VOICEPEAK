import discord
import os
import logging
import re
from voice_synthesizer import VoiceSynthesizer

logger = logging.getLogger(__name__)
handler = logging.FileHandler('events.log')
handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

async def join_voice_channel(channel):
    try:
        await channel.connect()
    except Exception as e:
        logger.error(f"Failed to join voice channel: {e}")
        raise

async def leave_voice_channel(guild, bot=None):
    try:
        if guild.voice_client is not None:
            await guild.voice_client.disconnect()
            if bot is not None:
                bot.volume = 1.0
                bot.reset_emotion()
    except Exception as e:
        logger.error(f"Failed to leave voice channel: {e}")
        raise

async def synthesize_and_play(message, voice_synthesizer, word_dictionary, ffmpeg_executable_path, volume=1.0):
    try:
        # ユーザーメンションを表示名に置き換え
        for user in message.mentions:
            message.content = message.content.replace(f'<@{user.id}>', user.display_name)
            message.content = message.content.replace(f'<@!{user.id}>', user.display_name)

        # ロールメンションをロール名に置き換え
        for role in message.role_mentions:
            message.content = message.content.replace(f'<@&{role.id}>', role.name)

        # チャンネルメンションをチャンネル名に置き換え
        for channel in message.channel_mentions:
            message.content = message.content.replace(f'<#{channel.id}>', f'#{channel.name}')
        
        # message.contentにURLが含まれている場合、URLを「URL省略」に置き換え
        message.content = re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', 'URL省略', message.content)
        
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
    except Exception as e:
        logger.error(f"Failed to synthesize and play: {e}")
        raise