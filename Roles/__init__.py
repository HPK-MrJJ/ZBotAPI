from .Roles import Roles


async def setup(bot):
    await bot.add_cog(Roles(bot))
