import asyncio

import discord
from discord.ext import commands


class Fun:
    """
    Fun and useful stuff
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def marco(self, ctx):
        """
        Says "polo"
        """
        await self.bot.say(self.bot.msg_prefix + "polo")

    @commands.command(pass_context=True)
    async def soon(self, ctx, *, message: str = ""):
        """
        Makes a soon tm
        """
        await self.bot.delete_message(ctx.message)
        await self.bot.say("soon\u2122" + message)

    @commands.command(pass_context=True)
    async def give(self, ctx, *, message: str = ""):
        """
        Gives stuff
        """
        await self.bot.delete_message(ctx.message)
        await self.bot.say("༼ つ ◕\\_◕ ༽つ " + message + " ༼ つ ◕\\_◕ ༽つ")

    @commands.command(pass_context=True)
    async def shrug(self, ctx, *, message: str = ""):
        """
        Makes a shrug
        """
        await self.bot.delete_message(ctx.message)
        await self.bot.say("¯\_(ツ)_/¯ " + message)

    @commands.command(pass_context=True)
    async def lenny(self, ctx, *, message: str = ""):
        """
        Makes a lenny face
        """
        await self.bot.delete_message(ctx.message)
        await self.bot.say("( ͡° ͜ʖ ͡°) " + message)

    @commands.command(pass_context=True, aliases=["d"])
    async def justdeleteme(self, ctx, count: int):
        """
        Deletes 'count' number of message you have sent in the channel

        But only if they are in the first 1000 messages
        """
        count += 1
        iterator = self.bot.logs_from(ctx.channel, limit=1000)
        async for m in iterator:
            if isinstance(m, discord.Message):
                if (m.author == ctx.author):
                    await self.bot.delete_message(m)
                    count -= 1
                    if count <= 0:
                        return

    @commands.command(pass_context=True, hidden=True)
    async def whois(self, ctx, *, ingnore: str = ""):
        """
        Let's just ingore that
        """
        to_del = await self.bot.say(self.bot.msg_prefix + "Use debug...")
        await asyncio.sleep(5)
        await self.bot.delete_message(to_del)

    def _calculate_mutual_servers(self, member: discord.Member):
        # Calculates mutual servers.
        serverlist = []
        for server in self.bot.servers:
            assert isinstance(server, discord.Server)
            if server.get_member(member.id):
                serverlist += [server.name]
        return serverlist

    def _safe_roles(self, roles: list):
        names = []
        for role in roles:
            if role.name == "@everyone":
                names.append("@\u200beveryone")  # u200b is invisible space
            else:
                names.append(role.name)

        return names


def setup(bot):
    bot.add_cog(Fun(bot))
