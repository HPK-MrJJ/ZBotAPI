from redbot.core import commands as red_commands
from discord.ext import commands as discord_commands
import discord

def is_owner_overridable():
    # Similar to @commands.is_owner()
    # Unlike that, however, this check can be overridden with core Permissions
    def predicate(ctx):
        return False
    return red_commands.permissions_check(predicate)
    
class Roles(discord_commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @is_owner_overridable()    
    @discord_commands.command()
    async def add_role(self, ctx, role, username):
        await ctx.send(f"Adding role {role} to user {username} now!")
        
        try:
            var = discord.utils.get(ctx.guild.roles, name=role)
            if var is None:
                raise ValueError("Role not found.")
        except Exception as e:
            await ctx.send(f"{e}\n Please give a valid role name.")
            return
        
        member = ctx.guild.get_member_named(username) # Member object that you want to add the role to
        if member is None:
            await ctx.send(f"Member {username} not found.")
            return
        
        await member.add_roles(var) # Adds the role to the member
        await ctx.send(f"Role {role} has been added to {username}.")
