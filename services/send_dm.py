import discord

async def send_dm(bot, user_id: int, body: str or discord.Embed, emojis: list or None):
    user = bot.get_user(user_id)
    channel = user.dm_channel

    if channel is None:
        channel = await user.create_dm()
    if type(body) is discord.Embed:
        message = await channel.send(embed=body)
    elif type(body) is str:
        message = await channel.send(body)
    else:
        raise Exception("Private message must contain body")
    if emojis:
        for emoji in emojis:
            await message.add_reaction(emoji)
            
    return message