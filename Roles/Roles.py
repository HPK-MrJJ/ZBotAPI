from redbot.core import commands
import discord

def is_owner_overridable():
    # Similar to @commands.is_owner()
    # Unlike that, however, this check can be overridden with core Permissions
    def predicate(ctx):
        return False
    return commands.permissions_check(predicate)
    
class Roles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @is_owner_overridable()    
    @commands.command(name="add_role")
    async def add_role(self,ctx,role):
        await ctx.send(f"adding role {role} to user {ctx.message.author} now!")
        try:
            var = discord.utils.get(ctx.guild.roles, name = role)
        except Exception as e:
            await ctx.send(f"{e}\n Please give a valid role name.") 
        member = ctx.message.author # Member object that you want to add the role to
        await member.add_roles(var) # Adds the role to the member
