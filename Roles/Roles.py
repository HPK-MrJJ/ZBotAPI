import re
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
    
    @red_commands.Cog.listener()
    async def on_message(self, message):
        first_char = message.content[0]
        ctx = await self.bot.get_context(message)
        if not first_char.isalpha():
            return

        # Check if the message contains the trigger phrase
        if 'fuck you zalora-bot' in message.content.lower():
            await message.reply('Well fuck you too!')
            
        if 'best wishes to montrandec' in message.content.lower() or 'best wishes to r9238yfh' in message.content.lower():
            await message.reply('Amen, may he soon return to the Fund with a trouble-free mind.')

        if message.channel.id == 1202487727635832862: #This is the id of the share-report channel
            if 'share report as of ' in message.content.lower():
                
                # This pattern isolates blocks in the share-report for each shareholder assuming bolded names
                pattern = r'\*\*(\w+(?:\s+\w+)*)\*\*\nTotal Stake: \d+%\n# of Shares: (\d+\.\d+)'

                # Find all matches in the content
                matches = re.findall(pattern, message.content, re.IGNORE_CASE)
                
                for match in matches:
                    if ' - ' in match[0]: # the ' - ' is used to separate nation name from server name when they differ. {nation name} - {server name}
                        name = match[0].split(' - ')[1].strip().lower()
                    else:
                        name = match[0]  # server name
                    amount = float(match[1]) # number of shares

                    # Assign the appropriate roles depending on the number of shares. Always check for investor and then only add the highest subsequent role.
                    member_roles = message.guild.get_member(message.author.id).roles
                    if amount > 0 and amount < 10 and not any(role.name == 'Investor' for role in member_roles :
                        await add_role(ctx.guild, ctx.channel, 'Investor', name)
                        role_changed_to = 'Investor'
                    if amount >= 10 and amount < 100 and not any(role.name == 'Bronze' for role in member_roles:
                        await add_role(ctx.guild, ctx.channel, 'Bronze', name)
                        role_changed_to = 'Bronze'
                        role_purged = await purge_roles(ctx.guild, name)
                    elif amount >= 100 and amount < 500 and not any(role.name == 'Silver' for role in member_roles:
                        await add_role(ctx.guild,ctx.channel, 'Silver', name)
                        role_changed_to = 'Silver'
                        role_purged = await purge_roles(ctx.guild, name)
                    elif amount >= 500 and amount < 1000 and not any(role.name == 'Gold' for role in member_roles:
                        await add_role(ctx.guild,ctx.channel, 'Gold', name)
                        role_changed_to = 'Gold'
                        role_purged = await purge_roles(ctx.guild, name)
                    elif amount >= 1000 and amount < 2000 and not any(role.name == 'Platinum' for role in member_roles:
                        await add_role(ctx.guild,ctx.channel, 'Platinum', name)
                        role_changed_to = 'Platinum'
                        role_purged = await purge_roles(ctx.guild, name)
                    elif amount >= 2000 and not any(role.name == 'Plutonium' for role in member_roles:
                        await add_role(ctx.guild,ctx.channel, 'Plutonium', name)
                        role_changed_to = 'Plutonium'
                        role_purged = await purge_roles(ctx.guild, name)
                    
                    # find the bot-action-logs channel 
                    channel = discord.utils.get(message.guild.channels, name="bot-actions-log")

                    # log the role change
                    if role_purged:
                        await message.channel.send(f'Assigned {role_changed_to} to {name}.') if role_purged != '' else message.channel.send(f'Switched {name} from {role_purged} to {role_changed_to}.')
                    
