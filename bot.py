import inspect
import json
import logging
import os
import traceback
import sys
from datetime import datetime


import logbook
from discord.ext import commands

if not os.path.isfile("config.json"):
    import shutil

    shutil.copyfile("example-config.json", "config.json")

with open("config.json") as file_in:
    config = json.load(file_in)

bot = commands.Bot(command_prefix=config['prefix'], description="Selfbot by LittleEndu", self_bot=True)

if not os.path.isdir("logs"):
    os.makedirs("logs")
bot.config = config
bot.logger = logbook.Logger("Selfbot")
bot.logger.handlers.append(
    logbook.FileHandler("logs/" + str(datetime.now().date()) + ".log", level="INFO", bubble=True))
bot.logger.handlers.append(logbook.StreamHandler(sys.stderr, level='INFO', bubble=True))
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
        await bot.send_message(ctx.message.channel, ":question:")
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
    if config['info_msg'] is None:
        msg = "https://github.com/LittleEndu/Little-Discord-Selfbot"
    else:
        msg = config['info_msg']
    await bot.say("\U0001f916 "+msg)

@bot.command(pass_context=True, hidden=True, aliases=['exit', 'stop', 'die'])
async def quit(ctx):
    """
    Stops the bot
    """
    await bot.say("\U0001f916 \U0001f52b")
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
            await bot.say('\U0001f916 Failed to reload extension ``%s``' % i)
            fail = True
    if fail:
        await bot.say('\U0001f916 Reloaded remaining extensions.')
    else:
        await bot.say('\U0001f916 Reloaded all extensions.')

@bot.command(pass_context=True, hidden=True)
async def load(ctx, *, extension: str):
    """
    Load an extension.
    """
    try:
        bot.load_extension("cogs.{}".format(extension))
    except Exception as e:
        bot.logger.error("".join(traceback.format_exception(type(e), e.__cause__, e.__traceback__)))
        await bot.say("\U0001f916 Could not load `{}` -> `{}`".format(extension, e))
    else:
        await bot.say("\U0001f916 Loaded cog `{}`.".format(extension))


@bot.command(pass_context=True, hidden=True)
async def unload(ctx, *, extension: str):
    """
    Unload an extension.
    """
    try:
        bot.unload_extension("{}".format(extension))
    except Exception as e:
        bot.logger.error("".join(traceback.format_exception(type(e), e.__cause__, e.__traceback__)))
        await bot.say("\U0001f916 Could not unload `{}` -> `{}`".format(extension, e))
    else:
        await bot.say("\U0001f916 Unloaded `{}`.".format(extension))


@bot.command(pass_context=True, hidden=True)
async def debug(ctx, *, command: str):
    """
    Run a debug command.
    """
    try:
        result = eval(command)
        if inspect.isawaitable(result):
            result = await result
    except Exception as e:
        result = repr(e)
    if config["token"] in str(result):
        fmt = "Doing this would reveal my token!!!"
    else:
        fmt = "```xl\nInput: {}\nOutput: {}\nOutput class: {}```".format(command, result, result.__class__.__name__)
    await bot.edit_message(ctx.message, new_content=fmt)

if __name__ == '__main__':
    if config["token"]:
        for extension in config['auto_load']:
            try:
                bot.load_extension(extension)
                bot.logger.info("Successfully loaded {}".format(extension))
            except Exception as e:
                bot.logger.info('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))
        bot.logger.info("Logging in...\n\n\n")
        bot.run(config['token'], bot=False)
    else:
        bot.logger.info("Please add the bot's token to the config file!")
