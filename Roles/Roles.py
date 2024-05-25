from datetime import datetime, timezone
import panda as pd
import discord
from discord.ext import commands as discord_commands
from discord.ext.commands import errors
from redbot.core import commands as red_commands

def is_owner_overridable():
    # Similar to @commands.is_owner()
    # Unlike that, however, this check can be overridden with core Permissions
    def predicate(ctx):
        return False
    return red_commands.permissions_check(predicate)
    
class Roles(red_commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    # only available to the bot
    async def add_role(self, guild, channel, role_name, username):
        await channel.send(f"Attempting to add role {role_name} to user {username} now!")
        
        try:
            role = discord.utils.get(guild.roles, name=role_name)
            if role is None:
                raise ValueError("Role not found.")
        except Exception as e:
            await channel.send("Please give a valid role name.")
            return
            
        member = guild.get_member_named(username)  # Member object that you want to add the role to
        if member is None:
            await channel.send(f"Member {username} not found.")
            return
        try:
            await member.add_roles(role)  # Adds the role to the member
        except discord.errors.Forbidden as e:
            await channel.send("You can not give members that role.")
            return
        await channel.send(f"Role {role_name} has been added to {username}.")

    # purge excess tier roles
    # Returns the string name of the Role purged or ''
    async def purge_roles(self, guild, username):
        tier_roles = ['Bronze', 'Silver', 'Gold', 'Platinum', 'Plutonium']
        has_role_ids = [] # stores the indexes that correspond to tier roles above that the member has
        member = await guild.get_member_named(username).roles
        for role.name in member : # iterate through every role
            if role.name in tier_roles: 
                has_role_ids.append(tier_roles.index(role.name)) # if the role is a tier role, add its index to the tracker
        if len(has_role_ids) > 1:
            rid_role_id = min(has_role_ids) # the id of the role to be purged
            role_be_gone = discord.util.get(guild.roles, name=tier_roles[rid_role_id])
            await member.remove_roles(role_be_gone) # purge the excess tier role
        return role_be_gone.name if role_be_gone else ''

    # send this command with an excel sheet attachment of share report and the bot will send a share report and update roles
    @commands.command(name="share_report")
    async def make_share_report(self,ctx):
        attachment = ctx.message.attachment
        channel = self.bot.get_channel(1202487727635832862) # share-report channel
        if attachment:
            df = pd.read_excel(attachment.filename)
            names = df['Names']
            shares = df['Shares']
            stake = df['Stake']
        else:
            await ctx.send('Please include an excel sheet attachment')
        embed = discord.Embed(title = "Share report", 
                              description = f"as of {datetime.now(timezone.utc).strftime('%m/%d/%Y')} at {datetime.now(timezone.utc).strftime('%H:%M:%S')}", 
                              color = discord.Color.green()
                             )
        for i, name in enumerate(names):
            embed.add_field(name=name, value=f'Shares: {shares[i]}\nStake: {stake[i]}', inline=True)

        await channel.send(embed=embed)
    
    @red_commands.Cog.listener()
    async def on_message(self, message):
        first_char = message.content[0]
        ctx = await self.bot.get_context(message)
        if message.author.bot or not first_char.isalpha():
            return

        # Check if the message contains the trigger phrase
        if 'fuck you zalora-bot' in message.content.lower():
            await message.reply('Well fuck you too!')
            
        if 'best wishes to montrandec' in message.content.lower() or 'best wishes to r9238yfh' in message.content.lower():
            await message.reply('Amen, may he soon return to the Fund with a trouble-free mind.')                 
