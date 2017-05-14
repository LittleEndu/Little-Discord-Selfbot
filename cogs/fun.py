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

    @commands.command(pass_context=True)
    async def whois(self, ctx, *, member: discord.Member):
        """
        Info about member
        """
        if ctx.message.author.permissions_in(ctx.message.channel).embed_links:
            em = discord.Embed(title="WHOIS for user {}#{}".format(member.name, member.discriminator),
                               color=member.color)
            if member.display_name != member.name:
                em.add_field(name="Display name", value=member.display_name)
            em.add_field(name="Created at", value=str(member.created_at))
            em.add_field(name="Joined at", value=str(member.joined_at))
            em.add_field(name="Color", value=str(member.color))
            await self.bot.send_message(ctx.message.channel, embed=em)
        else:
            msg = self.bot.msg_prefix + """WHOIS for user {m}:

```xl
Username: {member.name}#{member.discriminator}
Display name: {member.display_name}
User ID: {member.id}
Colour: {member.colour}
Created: {cr}
Joined: {jr}```""".format(m=str(member), member=member, cr=member.created_at, jr=member.joined_at)
            await self.bot.say(msg)

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
