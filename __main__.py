import traceback
import config
import discord
import os
from discord.ext import commands
from datetime import datetime

intents = discord.Intents().all()

bot = commands.Bot(command_prefix=config.bot_prefix
                   , description=config.bot_description
                   , owner_id=config.owner_id,
                   intents=intents)


@bot.command(name="ping", aliases=['check-ms'])
async def do_ping(ctx):
    await ctx.send(f'Pong :ping_pong: ! {round(bot.latency * 1000)} ms ')


if __name__ == '__main__':

    for cog in os.listdir("./cogs"):
        try:
            cog = f"cogs.{cog}"
            bot.load_extension(cog)
        except Exception as e:
            print(f"{cog} Can not be loaded")
            raise e


    @bot.event
    async def on_ready():
        print(f'We have logged in as {bot.user}'
              f'\nVersion: {discord.__version__} '
              f'\nSuccessfully logged in and booted!'
              f'\nTime: [{datetime.now().strftime("%H:%M:%S")}]')


    bot.run(config.bot_token)
