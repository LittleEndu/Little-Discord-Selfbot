import asyncio

import discord
from discord.ext import commands


class Fun:
    """
    Fun and useful stuff
    """

    def __init__(self, bot: commands.Bot):
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
        iterator = self.bot.logs_from(ctx.message.channel, limit=1000)
        async for m in iterator:
            if m.author == self.bot.user:
                await self.bot.delete_message(m)
                count -= 1
                if count <= 0:
                    return

    async def ask(self, question: str):
        to_del = await self.bot.say(self.bot.msg_prefix + question)
        await asyncio.sleep(0.5)
        response = await self.bot.wait_for_message(author=self.bot.user)
        string = response.content
        await self.bot.delete_message(to_del)
        await self.bot.delete_message(response)
        return string

    @commands.command(pass_context=True)
    async def nukemeplease(self, ctx):
        """
        Deletes all your messages from this channel
        """
        string = await self.ask("This will delete all your messages from this channel. Are you sure you want to continue? Say ``yes`` to continue...")
        if not string.lower().startswith("y"):
            to_del = await self.bot.say(self.bot.msg_prefix + "Oki... Aborting...")
            await asyncio.sleep(5)
            await self.bot.delete_message(to_del)
            return

        date = None
        iterator = self.bot.logs_from(ctx.message.channel, limit=5000)
        while True:
            count = 0
            async for m in iterator:
                count += 1
                date = m.timestamp
                if m.author == self.bot.user:
                    await self.bot.delete_message(m)
                    await asyncio.sleep(0.5)
            if count == 0:
                break
            iterator = self.bot.logs_from(ctx.message.channel, limit=5000, before=date)


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


def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))
