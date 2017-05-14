import asyncio
import html
import re

import aiohttp
import async_timeout
import dateutil.parser
import discord
from bs4 import BeautifulSoup as BS
from discord.ext import commands


class Mal:
    def __init__(self, bot):
        self.bot = bot
        self.LINK_ANIME_SEARCH = "https://myanimelist.net/anime.php?q={}"
        self.LINK_MANGA_SEARCH = "https://myanimelist.net/manga.php?q={}"

    def scrape_searchresults(self, soup: BS, is_anime=True):
        return soup.find("div", attrs={"class": "js-categories-seasonal js-block-list list"}) \
            .find_all("a", attrs={"class": "hoverinfo_trigger fw-b{}".format(" fl-l" if is_anime else "")})

    def process_single_soup(self, soup):
        anime_name = soup.find("span", attrs={"itemprop": "name"}).string
        args = {"name": anime_name, "aliases": [anime_name]}
        for i in soup.find("td", attrs={"class": "borderClass", "width": "225"}).find_all("div"):
            darktext = i.find("span", attrs={"class": "dark_text"})
            if darktext:
                if darktext.string == "English:":
                    args["aliases"].append(darktext.parent.text.split(":")[-1].strip())
                    args["english"] = darktext.parent.text.split(":")[-1].strip()
                elif darktext.string == "Japanese:":
                    args["aliases"].append(darktext.parent.text.split(":")[-1].strip())
                elif darktext.string == "Type:":
                    args["type"] = darktext.parent.text.split(":")[-1].strip()
                elif darktext.string == "Episodes:":
                    try:
                        args["episodes"] = int(darktext.parent.text.split(":")[-1].strip())
                    except:
                        args["episodes"] = None
                elif darktext.string == "Status:":
                    args["status"] = darktext.parent.text.split(":")[-1].strip()
                elif darktext.string == "Aired":
                    aired_parts = darktext.parent.text.split(":")[-1].strip().split(" to ")
                    if len(aired_parts) == 1:
                        try:
                            args["airedfrom"] = dateutil.parser.parse(aired_parts[0])
                        except:
                            args["airedfrom"] = None
                    else:
                        try:
                            args["airedfrom"] = dateutil.parser.parse(aired_parts[0])
                            args["airedto"] = dateutil.parser.parse(aired_parts[1])
                        except:
                            args["airedfrom"] = None
                            args["airedto"] = None
                elif darktext.string == "Premiered:":
                    args["premiered"] = darktext.parent.text.split(":")[-1].strip()
                elif darktext.string == "Producers:":
                    ids = []
                    for a in darktext.parent.find_all("a"):
                        ids.append(a.get("href").split("/")[-2])
                    args["producers"] = ids
                elif darktext.string == "Licensors:":
                    if "None found" in darktext.parent.text:
                        args["licensors"] = []
                        continue
                    ids = []
                    for a in darktext.parent.find_all("a"):
                        ids.append(a.get("href").split("/")[-2])
                    args["licensors"] = ids
                elif darktext.string == "Studios:":
                    ids = []
                    for a in darktext.parent.find_all("a"):
                        ids.append(a.get("href").split("/")[-2])
                    args["studios"] = ids
                elif darktext.string == "Source:":
                    args["source"] = darktext.parent.text.split(":")[-1].strip()
                elif darktext.string == "Genres:":
                    ids = []
                    for a in darktext.parent.find_all("a"):
                        ids.append(a.get("href").split("/")[-2])
                    args["genres"] = ids
                elif darktext.string == "Duration:":
                    duration_text = darktext.parent.text.split(":")[-1].strip()
                    duration_mins = 0
                    for part in duration_text.split("."):
                        part_match = re.findall('(\\d+)', part)
                        if not part_match:
                            continue
                        part_volume = int(part_match[0])
                        if part.endswith('hr'):
                            duration_mins += part_volume * 60
                        elif part.endswith('min'):
                            duration_mins += part_volume
                    args["duration"] = duration_mins
                elif darktext.string == "Rating:":
                    args["rating"] = darktext.parent.text.split(":")[-1].strip()
                elif darktext.string == "Score:":
                    try:
                        args["score"] = float(darktext.parent.text.split(":")[-1].split("(")[0].strip())
                    except:
                        args["score"] = None
        synopsis = soup.find("span", attrs={"itemprop": "description"})
        args['synopsis'] = synopsis.text
        thumbnail_link = soup.find("img", attrs={"itemprop": "image", "class": "ac"}).get("src")
        args['thumbnail_link'] = thumbnail_link
        return args

    async def mal_search(self, search_query: str, link: str = None, is_anime=True):
        if not link:
            if is_anime:
                link = self.LINK_ANIME_SEARCH
            else:
                link = self.LINK_MANGA_SEARCH
        search_query = html.escape(search_query.replace(" ", "+"))
        async with aiohttp.ClientSession() as session:
            with async_timeout.timeout(10):
                async with session.get(link.format(search_query)) as response:
                    soup = BS(await response.read(), "lxml")
                    results = [(i.get("href"), i.string) for i in self.scrape_searchresults(soup, is_anime)]
                    formated = list()
                    for r in results:
                        formated.append((r[0].split("/")[-2], r[1], r[0]))
                    async with session.get(formated[0][2]) as response2:
                        soup = BS(await response2.read(), "lxml")
                    return formated

    async def get_soup(self, link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as response:
                return BS(await response.read())

    @commands.command(pass_context=True)
    async def findanime(self, ctx, *, search_for: str):
        """
        Searches and displays anime
        """
        to_del = await self.bot.say(self.bot.msg_prefix + "Searching \U0001f30f \U0001f50d")
        results = await self.mal_search(search_for)
        anime_info = self.process_single_soup(await self.get_soup(results[0][2]))
        em = discord.Embed(description=results[0][2])
        em.set_thumbnail(url=anime_info['thumbnail_link'])
        if anime_info['episodes']:
            em.add_field(name="Episodes", value=anime_info['episodes'])
        if anime_info['score']:
            em.add_field(name="Score", value=anime_info['score'])
        em.add_field(name="Status", value=anime_info['status'])
        await self.bot.send_message(ctx.message.channel, embed=em)
        await self.bot.delete_message(to_del)


def setup(bot):
    bot.add_cog(Mal(bot))
