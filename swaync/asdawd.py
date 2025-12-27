import nexcord
from nexcord.ext import commands
import yt_dlp
import asyncio

intents = nexcord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Настройки для yt-dlp
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

class YTDLSource(nexcord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(nexcord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)

@bot.event
async def on_ready():
    print(f'Бот {bot.user} готов к работе!')

@bot.command(name='play', aliases=['p', 'играть'])
async def play(ctx, *, url):
    """Воспроизводит музыку по URL (YouTube, SoundCloud и т.д.)"""
    
    # Проверяем, находится ли пользователь в голосовом канале
    if not ctx.author.voice:
        await ctx.send('❌ Вы должны находиться в голосовом канале!')
        return

    channel = ctx.author.voice.channel

    # Подключаемся к каналу, если еще не подключены
    if ctx.voice_client is None:
        await channel.connect()
    elif ctx.voice_client.channel != channel:
        await ctx.voice_client.move_to(channel)

    # Останавливаем текущее воспроизведение, если оно есть
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    async with ctx.typing():
        try:
            player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'Ошибка: {e}') if e else None)
            await ctx.send(f'🎵 Сейчас играет: **{player.title}**')
        except Exception as e:
            await ctx.send(f'❌ Ошибка при воспроизведении: {str(e)}')

@bot.command(name='stop', aliases=['s', 'стоп'])
async def stop(ctx):
    """Останавливает воспроизведение и отключает бота"""
    
    if ctx.voice_client is None:
        await ctx.send('❌ Бот не подключен к голосовому каналу!')
        return

    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
    
    await ctx.voice_client.disconnect()
    await ctx.send('⏹️ Воспроизведение остановлено, бот отключен!')

@bot.command(name='pause', aliases=['пауза'])
async def pause(ctx):
    """Ставит воспроизведение на паузу"""
    
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send('⏸️ Воспроизведение приостановлено!')
    else:
        await ctx.send('❌ Сейчас ничего не играет!')

@bot.command(name='resume', aliases=['продолжить'])
async def resume(ctx):
    """Возобновляет воспроизведение"""
    
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send('▶️ Воспроизведение возобновлено!')
    else:
        await ctx.send('❌ Воспроизведение не на паузе!')

# Замените YOUR_BOT_TOKEN на токен вашего бота
bot.run('YOMTAyMjkzNzM4NDYwNzgxMzcyMg.G3UxKT.GqTJsRtjwOIe-N0lJnjy6BHaRiOOXoobt-iYnA')