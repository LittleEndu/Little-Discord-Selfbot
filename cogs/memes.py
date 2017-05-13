"""
Meme responses
"""
import asyncio
import json
import os
import random

import aiohttp
import discord
from discord.ext import commands


class Memes:
    """
    idk, it does meme stuff
    """

    def __init__(self, bot):
        self.IMGUR_API_LINK = "https://api.imgur.com/3/image"
        self.bot = bot
        self.config = bot.config
        if os.path.isfile("memes.json"):
            with open("memes.json") as meme_file:
                self.memes = json.load(meme_file)
        else:
            self.memes = list()

    def save_memes(self):
        with open("memes.json", "w") as file_out:
            json.dump(self.memes, file_out)

    def normalize(self, string: str):
        return string.replace("'", "").replace("fuck", "fck").lower()

    def find_best_meme(self, search_for):
        memes = []
        search_tags = self.normalize(search_for).split()
        for meme in self.memes:
            assert isinstance(meme, dict)
            will_add = True
            for s_tag in search_tags:
                is_in = False
                for instant in meme.get('instants', list()):
                    if s_tag in instant:
                        return [meme]
                for m_tag in meme['tags']:
                    if s_tag in m_tag:
                        is_in = True
                if not is_in:
                    will_add = False
            if will_add:
                memes.append(meme)

        return memes

    def has_instants(self, search_for):
        search_tags = search_for.split()
        for meme in self.memes:
            assert isinstance(meme, dict)
            for instant in meme.get('instants', list()):
                for stag in search_tags:
                    if stag in instant:
                        return True
        return False

    async def ask(self, ctx, question: str):
        to_del = await self.bot.say(self.bot.msg_prefix + question)
        await asyncio.sleep(1)
        response = await self.bot.wait_for_message(author=ctx.message.author)
        string = response.content
        await self.bot.delete_message(to_del)
        await self.bot.delete_message(response)
        return string

    @commands.command(pass_context=True, aliases=["addmeme"])
    async def savememe(self, ctx, url: str = ""):
        """
        Saves the uploaded image
        """
        if len(ctx.message.attachments) > 0 or url:
            if len(ctx.message.attachments) > 0:
                url = ctx.message.attachments[0]['url']
            async with aiohttp.ClientSession() as session:
                async with session.post(self.IMGUR_API_LINK,
                                        params={'image': url, 'type': "URL"},
                                        headers={"Authorization": "Client-ID {}".format(
                                            self.config['imgur_client_id'])}) as response:
                    response_json = json.loads(await response.text())
                    response_tags = await self.ask(ctx, "Please give tags")
                    if len(response_tags) > 0:
                        tags = self.normalize(response_tags).split()
                    else:
                        await self.bot.say(self.bot.msg_prefix + "No tags given... Aborting...")
                        return
                    info = {'tags': tags,
                            'delete_hash': response_json['data']['deletehash'],
                            'width': response_json['data']['width'],
                            'height': response_json['data']['height'],
                            'id': response_json['data']['id'],
                            'link': response_json['data']['link']}
                    self.memes.append(info)
                    self.save_memes()
                    to_del = await self.bot.say(self.bot.msg_prefix + "\U0001f44d")
                    await asyncio.sleep(5)
                    await self.bot.delete_message(to_del)
                    await self.bot.delete_message(ctx.message)
        else:
            self.bot.say(self.bot.msg_prefix + "You didn't include an image...")

    @commands.command(pass_context=True)
    async def removememe(self, ctx, *, search_for: str):
        """
        Will remove all memes it finds
        """
        memes = self.find_best_meme(search_for)
        if memes:
            if len(memes) > 1:
                await self.bot.say(self.bot.msg_prefix + "That returned more than one meme... Aborting...")
                return
            meme = memes[0]
            self.memes.remove(meme)
            async with aiohttp.ClientSession() as session:
                async with session.delete(self.IMGUR_API_LINK + "/{}".format(meme['delete_hash']),
                                          headers={"Authorization": "Client-ID {}".format(
                                              self.config['imgur_client_id'])}) as response:
                    response_json = json.loads(await response.text())
                    if response_json['success']:
                        await self.bot.say(self.bot.msg_prefix + "Successfully deleted")
                    else:
                        await self.bot.say(self.bot.msg_prefix + "Local pointer deleted, imgur refused to delete...")
            self.save_memes()
        else:
            await self.bot.say(self.bot.msg_prefix + "Didn't find such meme")

    @commands.command(pass_context=True)
    async def meme(self, ctx, *, search_for: str):
        """
        meme response
        """
        memes = self.find_best_meme(search_for)
        if memes:
            index = random.randint(0, len(memes) - 1)
            if ctx.message.author.permissions_in(ctx.message.channel).embed_links:
                em = discord.Embed()
                em.set_image(url=memes[index]['link'])
                await self.bot.send_message(ctx.message.channel, embed=em)
            else:
                await self.bot.say(self.bot.msg_prefix + memes[index]['link'])
            await asyncio.sleep(5)
            await self.bot.delete_message(ctx.message)
            self.memes[index]['usage'] = self.memes[index].setdefault('usage', 0) + 1
        else:
            await self.bot.say(self.bot.msg_prefix + "Unable to find meme")

    @commands.command(pass_context=True, aliases=["addinstantmeme"])
    async def makeinstantmeme(self, ctx):
        """
        Will make instant access string for meme
        """
        string = await self.ask(ctx, "What to search for?")
        if not string:
            await self.bot.say(self.bot.msg_prefix + "Please specify string... Aborting...")
            return
        memes = self.find_best_meme(string)

        if len(memes) > 10:
            await self.bot.say(self.bot.msg_prefix + "That returned too many memes... Aborting...")
            return

        index = 0
        if len(memes) > 1:
            mmm = "\n"
            counter = 0
            for meme in memes:
                mmm += "{}: {}\n".format(counter, meme['tags'])
            string = await self.ask(ctx, "Choose what meme" + mmm)
            try:
                index = int(string)
            except:
                await self.bot.say(self.bot.msg_prefix + "Unable to convert to int... Aborting...")
                return

        assert isinstance(self.memes, list)
        try:
            meme_index = self.memes.index(memes[index])
            meme = self.memes[meme_index]
        except ValueError:
            await self.bot.say(self.bot.msg_prefix + "Meme found was not in memes???")
            return
        string = await self.ask(ctx, "What will be used for instant access?")
        for s in string.split():
            if self.has_instants(s):
                await self.bot.say(self.bot.msg_prefix + "Instant ``{}`` already in use.".format(s))
            else:
                meme.setdefault('instants', list()).append(s)
        self.memes[meme_index] = meme
        self.save_memes()
        await self.bot.say(self.bot.msg_prefix + "Added instants")

    @commands.command(pass_context=True)
    async def removeinstantmeme(self, ctx, search_for: str):
        """
        Removes instant access from meme
        """
        for meme in self.memes[:]:
            assert isinstance(meme, dict)
            if search_for in meme['instants']:
                assert isinstance(meme['instants'], list)
                index = self.memes.index(meme)
                try:
                    meme['instants'].remove(search_for)
                    self.memes[index] = meme
                    await self.bot.say(self.bot.msg_prefix + "Remove instant meme")
                    return
                except ValueError:
                    pass
        await self.bot.say(self.bot.msg_prefix + "Didn't find such meme")

    @commands.command(pass_context=True)
    async def listmemes(self, ctx, *, search_for: str = ""):
        """
        Lists memes
        """
        if search_for:
            memes = self.find_best_meme(search_for)
        else:
            memes = self.memes
        if not memes:
            await self.bot.say(self.bot.msg_prefix + "Unable to find anything")
            return
        mmm = self.bot.msg_prefix
        counter = 1
        for meme in memes:
            next_m = "``{}: {}``, ".format(counter, " ".join(meme['tags']))
            counter += 1
            if len(next_m + mmm) < 2000:
                mmm += next_m
            else:
                await self.bot.say(mmm[:-2])
                mmm = self.bot.msg_prefix + next_m
        await self.bot.say(mmm[:-2])

    @commands.command(pass_context=True)
    async def cleanmemes(self, ctx):
        """
        Cleans memes
        """
        tag_changes = []
        for meme in self.memes:
            assert isinstance(meme, dict)
            final_tags = meme['tags']
            for tag1 in final_tags[:]:
                one_skip = True
                for tag2 in final_tags[:]:
                    if tag1 == tag2:
                        if one_skip:
                            one_skip = False
                            continue
                    if tag1 in tag2:
                        final_tags.remove(tag1)
                        break
            index = self.memes.index(meme)
            tag_changes.append("``{} -> {}``".format(" ".join(meme['tags']), " ".join(final_tags)))
            self.memes[index]['tags'] = final_tags
        if tag_changes:
            self.save_memes()
            mmm = self.bot.msg_prefix + "Here are the memes I changed:\n"
            for change in tag_changes:
                next_m = change + ", "
                if len(mmm + next_m) < 2000:
                    mmm += next_m
                else:
                    await self.bot.say(mmm[:-2])
                    mmm = self.bot.msg_prefix + next_m
            await self.bot.say(mmm[:-2])
        else:
            await self.bot.say(self.bot.msg_prefix + "All memes are already clean")

def setup(bot):
    bot.add_cog(Memes(bot))
