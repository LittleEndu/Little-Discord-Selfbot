import asyncio
import inspect
import json
import logging
import os
import sys
import traceback
from datetime import datetime

import logbook
from discord.ext import commands

if not os.path.isfile("config.json"):
    import shutil

    shutil.copyfile("example-config.json", "config.json")

with open("config.json") as file_in:
    config = json.load(file_in)

bot = commands.Bot(command_prefix=config.get('prefix', "selfbot>"), description="Selfbot by LittleEndu", self_bot=True)

if not os.path.isdir("logs"):
    os.makedirs("logs")
bot.config = config
bot.msg_prefix = "\U0001f916 "
bot.logger = logbook.Logger("Selfbot")
bot.logger.handlers.append(
    logbook.FileHandler("logs/" + str(datetime.now().date()) + ".log", level="TRACE", bubble=True))
bot.logger.handlers.append(logbook.StreamHandler(sys.stderr, level='INFO', bubble=True))
bot.running_debug = False
logging.root.setLevel(logging.INFO)


@bot.event
async def on_ready():
    bot.logger.info('Logged in as')
    bot.logger.info(bot.user.name)
    bot.logger.info(bot.user.id)
    bot.logger.info('------')


@bot.event
async def on_message(message):
    await bot.process_commands(message)


@bot.event
async def on_command_error(e, ctx):
    # Check the type of the error.
    if ctx.message.author.id != bot.user.id:
        return
    if isinstance(e, (commands.errors.BadArgument, commands.errors.MissingRequiredArgument)):
        await bot.send_message(ctx.message.channel, ":x: Bad argument: {}".format(' '.join(e.args)))
        return
    elif isinstance(e, commands.errors.CheckFailure):
        await bot.send_message(ctx.message.channel,
                               ":x: Check failed. You probably don't have permission to do this.")
        return
    elif isinstance(e, commands.errors.CommandNotFound):
        await bot.send_message(ctx.message.channel, bot.msg_prefix + ":question:")
        return
    else:
        await bot.send_message(ctx.message.channel,
                               ":x: Error occurred while handling the command.")
        bot.logger.error("".join(traceback.format_exception(type(e), e.__cause__, e.__cause__.__traceback__)))


@bot.command(pass_context=True, hidden=True, aliases=['github'])
async def info(ctx):
    """
    Shows info
    """
    if not config.get('info_msg', ""):
        msg = "https://github.com/LittleEndu/Little-Discord-Selfbot"
    else:
        msg = config.get('info_msg', "No info")
    await bot.say(bot.msg_prefix + msg)


@bot.command(pass_context=True, hidden=True, aliases=['exit', 'stop', 'die'])
async def quit(ctx):
    """
    Stops the bot
    """
    await bot.say(bot.msg_prefix + "\U0001f52b")
    bot.logger.info("Exit by command...\n\n\n")
    os._exit(0)


@bot.command(pass_context=True, hidden=True, aliases=['reloadall'])
async def reload(ctx):
    """
    Reloads all modules.
    """
    utils = []
    for i in bot.extensions:
        utils.append(i)
    fail = False
    for i in utils:
        bot.unload_extension(i)
        try:
            bot.load_extension(i)
        except:
            await bot.say(bot.msg_prefix + "Failed to reload extension ``%s``" % i)
            fail = True
    if fail:
        await bot.say(bot.msg_prefix + "Reloaded remaining extensions.")
    else:
        await bot.say(bot.msg_prefix + "Reloaded all extensions.")


@bot.command(pass_context=True, hidden=True)
async def load(ctx, *, extension: str):
    """
    Load an extension.
    """
    try:
        bot.load_extension("cogs.{}".format(extension))
    except Exception as e:
        bot.logger.error("".join(traceback.format_exception(type(e), e.__cause__, e.__traceback__)))
        await bot.say(bot.msg_prefix + "Could not load `{}` -> `{}`".format(extension, e))
    else:
        await bot.say(bot.msg_prefix + "Loaded cog `{}`.".format(extension))


@bot.command(pass_context=True, hidden=True)
async def unload(ctx, *, extension: str):
    """
    Unload an extension.
    """
    try:
        bot.unload_extension("{}".format(extension))
    except Exception as e:
        bot.logger.error("".join(traceback.format_exception(type(e), e.__cause__, e.__traceback__)))
        await bot.say(bot.msg_prefix + "Could not unload `{}` -> `{}`".format(extension, e))
    else:
        await bot.say(bot.msg_prefix + "Unloaded `{}`.".format(extension))


@bot.command(pass_context=True, hidden=True)
async def debug(ctx, *, command: str):
    """
    Run a debug command.
    """
    if bot.running_debug:
        await bot.say(bot.msg_prefix + "You are doing this too fast \U0001F620 ")
        return
    try:
        result = eval(command)
        if inspect.isawaitable(result):
            bot.running_debug = True
            result = await result
    except Exception as e:
        result = repr(e)
    if config["token"] in str(result):
        fmt = command + "\n" + bot.msg_prefix + "Doing this would reveal my token!!!"
    else:
        fmt = "```xl\nInput: {}\nOutput: {}\nOutput class: {}```".format(command, result, result.__class__.__name__)
    await asyncio.sleep(0.5)
    await bot.edit_message(ctx.message, new_content=fmt)
    await asyncio.sleep(2)
    bot.running_debug = False


if __name__ == '__main__':
    bot.logger.info("\n\n\n")
    bot.logger.info("Initializing")
    if config.get('token', ""):
        for ex in config.get('auto_load', []):
            try:
                bot.load_extension(ex)
                bot.logger.info("Successfully loaded {}".format(ex))
            except Exception as err:
                bot.logger.info('Failed to load extension {}\n{}: {}'.format(ex, type(err).__name__, err))
        bot.logger.info("Logging in...")
        bot.run(config['token'], bot=False)
    else:
        bot.logger.info("Please add the token to the config file!")
