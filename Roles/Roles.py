import io
from datetime import datetime, timezone
import pandas as pd
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
    async def purge_roles(self, guild, username, new_role):
        tier_roles = ['Bronze', 'Silver', 'Gold', 'Platinum', 'Plutonium']
        has_role_ids = [] # stores the indexes that correspond to tier roles above that the member has
        member = await guild.get_member_named(username).roles
        for role.name in member : # iterate through every role
            if role.name in tier_roles: 
                has_role_ids.append(tier_roles.index(role.name)) # if the role is a tier role, add its index to the tracker
        if len(has_role_ids) > 1:
            for role in role_ids:
                if role != new_role:
                    str_role_be_gone = role
                    break
            role_be_gone = discord.util.get(guild.roles, name=str_role_be_gone)
            await member.remove_roles(role_be_gone) # purge the excess tier role
        return role_be_gone.name if role_be_gone else ''

    # send this command with an excel sheet attachment of share report and the bot will send a share report and update roles
    @is_owner_overridable()
    @red_commands.command(name="share_report")
    async def make_share_report(self,ctx):
        attachment = ctx.message.attachments[0]
        channel = self.bot.get_channel(1202487727635832862) # share-report channel
        if attachment: # Check for attachment and read the excel sheet
            attachment_data = await attachment.read()
            df = pd.read_excel(io.BytesIO(attachment_data))
            nations = df['Nation Name'] # nation name
            names = df['Server Name'] # discord username or NA if no discord account
            shares = df['Shares']
            stake = df['Stake']
        else:
            await ctx.send('Please include an excel sheet attachment')
            return
        embed = discord.Embed(title = "Share report", 
                              description = f"as of {datetime.now(timezone.utc).strftime('%m/%d/%Y')} at {datetime.now(timezone.utc).strftime('%H:%M:%S')} UTC", 
                              color = discord.Color.green()
                             )
        total = 0
        for i, nation in enumerate(nations):
            embed.add_field(name=nation, value=f'Shares: {shares[i]}\nStake: {stake[i]}%', inline=False)
            total += float(shares[i])
        embed.add_field(name='Total shares:', value=round(total,4),inline=False)

        await channel.send(embed=embed)

        channel = self.bot.get_channel(1243348183841505380) # bot-actions-log channel
        for i,name in enumerate(names):
            if name == 'NA':
                continue
            member = discord.utils.find(lambda m: m.name == name, ctx.guild.members)
            roles = member.roles
            roles_str = []
            for role in roles:
                roles_str.append(role.name)
            if 'Investor' not in roles_str: # always check for investor and then only the lowest tier
                await self.add_role(ctx.guild, ctx.channel, 'Investor', name)
                await channel.send(f'Added investor role to {name}.')
            if 'Bronze' not in roles_str and shares[i] < 100:
                await self.add_role(ctx.guild, ctx.channel, 'Bronze', name)
                await channel.send(f'Added bronze role to {name}.')
                tier_changed_to = 'Bronze'
            elif 'Silver' not in roles_str and shares[i] < 500 and shares[i] >= 100:
                await self.add_role(ctx.guild, ctx.channel, 'Silver', name)
                await channel.send(f'Added silver role to {name}.')
                tier_changed_to = 'Silver'
            elif 'Gold' not in roles_str and shares[i] < 1000 and shares[i] >= 500:
                await self.add_role(ctx.guild, ctx.channel, 'Gold', name)
                await channel.send(f'Added gold role to {name}.')
                tier_changed_to = 'Gold'
            elif 'Platinum' not in roles_str and shares[i] < 2000 and shares[i] >= 1000:
                await self.add_role(ctx.guild, ctx.channel, 'Platinum', name)
                await channel.send(f'Added platinum role to {name}.')
                tier_changed_to = Platinum
            elif 'Plutonium' not in roles_str and shares[i] >= 2000:
                await self.add_role(ctx.guild, ctx.channel, 'Plutonium', name)
                await channel.send(f'Added plutonium role to {name}.')
                tier_changed_to = Plutonium
            purged_role = await self.purge_roles(ctx.guild, name, tier_changed_to) # get rid of the old role if needed
            if purged_role != '':
                await channel.send(f'Removed {purged_role} from {name}')
                
    
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
