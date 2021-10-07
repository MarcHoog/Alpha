# Default
from datetime import datetime, timedelta

# APschedular
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

# discord
import discord
from discord.ext import commands

# local
from services.utc2local import utc2local
from services.send_dm import send_dm

lize = 285883793439457281
marc = 372820809548300289

class PillReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = ['👍','👎','🛑']
        self._scheduler = AsyncIOScheduler()
        self._scheduler.start()
        self._scheduler.add_job(self.reminder_job, CronTrigger(hour="04", minute="00", second="0"),args=[lize,])
 
    # Embeds
    # Made them propertys cause it's easy :P
    
    @property
    def reminder(self):
        _reminder = discord.Embed(title="Morning pillcheck ☕", 
                                  description=f"Your daily check 💊",
                                  color=0xffae00)
        _reminder.add_field(name="Yes", value=" :thumbsup:", inline=True)
        _reminder.add_field(name="No", value=" :thumbdown:", inline=True)
    
        return _reminder
 
    @property
    def thumbsup(self):
        _thumbsup = discord.Embed(title="c: You took your medication!",
                                  description="Keep it up Queen!",
                                  color=0x6cd586)
        
        return _thumbsup
        
    @property
    def thumbsdown(self):
        _thumbsdown = discord.Embed(title=":c noh... Tommorow you get another chance!",
                                    description="So you better! Better! Don't forget it tommorow",
                                    color=0xe64141)
        return _thumbsdown
        
    @property
    def timeout(self):
        _timeout = discord.Embed(title="This one timed out!",
                                 description="That's what they call an OOF... :frog: ",
                                 color=0xe11414)
        return _timeout
 
    # Schedular:
    
    # The standard job that sends the reminder and opens a timeoutjob for that message
    async def reminder_job(self,user_id):
        message = await send_dm(self.bot,user_id,self.reminder,['👍','👎'])
        future = datetime.now() + timedelta(hours=17)
        self._scheduler.add_job(self.timeout_job,DateTrigger(run_date=future),args=[message,])
    
    # the automatic time out job, this checks if the message needs to be timed down if the message is already deleted
    # it will just return and do nothing 
    # you can like remember the time out job per request and then close them but it's only for like one it doesn't matter 
    async def timeout_job(self,message):
        try:
            new_message = await message.channel.fetch_message(message.id)
        except discord.errors.NotFound:
            return
        
        if self._verify_title(new_message,'Morning pillcheck ☕') is False:
            return
        else:
            await self._timeout_response(new_message)
            

 
    # Gathering:
 
    # Returns discord.message from payload 
    async def get_message(self,payload):
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        return message

    # Checks:

    # Checks if bot \ dm \ emoji's
    def _verify_raw_reaction(self,payload) -> bool:
        if payload.user_id != self.bot.user.id \
            and payload.guild_id is None \
                and str(payload.emoji) in self.emoji:
                    return True
        else:
            return False
 
    # Checks if embed title is equal to
    @staticmethod
    def _verify_title(message,title:str) -> bool:
        if message.embeds[0].title == title:
            return True
        else:
            return False
                
    # Checks if message younger then 12 hours:
    async def _verify_message_age(self,message) -> bool:
        time_delta = (datetime.utcnow() - message.created_at)
        seconds = time_delta.total_seconds()
        hours = seconds // 3600
        if hours < 17:
            return True
        else:
            return False
                    

    # Responses
    
    # just to make standard reactions a little bit easier used for all expect time out
    @staticmethod
    async def _edit_embed(message,embed):
        await message.edit(embed=embed, delete_after=600)
    
    # normal response triggerd when everything is right! now just to see what is actually pressed
    async def _response(self,payload,message):
        if payload.emoji.name == '👍':
            await self._edit_embed(message,self.thumbsup)
            await self._notify_marc(message,'Taken 👍')
                    
        elif payload.emoji.name == '👎':
            await self._edit_embed(message,self.thumbsdown)
            await  self._notify_marc(message,'Forgotten 👎')
    
    # What the bot sends when there is a time out lil messy but works
    async def _timeout_response(self,message):
        await message.edit(embed=self.timeout)
        await message.remove_reaction('👍',self.bot.user)
        await message.remove_reaction('👎',self.bot.user)
        await message.add_reaction('🛑')
                
        await self._notify_marc(message,'Timed out 🛑')
    
    
    # Sends marc a DM from what the action was and what time the reminder was
    async def _notify_marc(self,message,action):
        timestamp = utc2local(message.created_at)
        embed = discord.Embed(title=action, 
                              description= f'This was the reminder from: {timestamp}', 
                              color=0xffae00)
        await  send_dm(self.bot,372820809548300289,body=embed,emojis=None)
    
    
    
    # Listener
    # the main thing this is what triggers when you do a reaction,
    # somethings you could define in more functions but i don't think that's truly needed for like 3 lines that you need to give options anyway 
    # so it becomes for lines again ya know what i mean
    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload: discord.raw_models.RawReactionActionEvent):
        if self._verify_raw_reaction(payload):
            message = await self.get_message(payload)
            if self._verify_title(message,'Morning pillcheck ☕'):
                if await self._verify_message_age(message):
                    await self._response(payload,message)
                else:
                    await self._timeout_response(message)
            elif self._verify_title(message,'This one timed out!'):
                if payload.emoji.name == '🛑':
                    await message.delete()     
        else:
            return
    
    
    
    # Commands
    
    # just for testing, triggers reminder job ( pybasses APSCHEDULER COMPLETELY)
    @commands.command()
    async def mailbox_test(self,ctx,user_id:int):
        await self.reminder_job(user_id)

def setup(bot):
    bot.add_cog(PillReminder(bot))
   