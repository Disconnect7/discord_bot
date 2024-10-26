import discord
import asyncio
import random
import my_file_parser as fp
from discord.ext import commands

# region variables declaration
repost_delay_s = 10

token = None
trusted_users = []
channels_to_repost = []

message_history_list = []

client = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# endregion

# region commands

# region for channel manipulation ___________________________

@client.command(name="тык")
async def tik(ctx):
    await ctx.send("!тык")

    await asyncio.sleep()


@client.command(name="show")
async def f(ctx):
    """выводит список доступных каналов для репоста"""

    await respond_to_message(ctx, response=f"Список серверов и каналов"
                                           f" для щитпостинга:")
    await show_text_channels(ctx)


@client.command(name="exclude")
async def f(ctx, *args):

    global channels_to_repost

    def get_channels_obj_from_args(args):
        tmp = []


        for index_str in args:
            try:
                tmp.append(channels_to_repost[int(index_str)])
            except IndexError:
                #если нет такого индекса - слакаем
                pass
        """
        int_args = [int(el) for el in args]
        exclude_list = [channels_to_repost[i] for i in int_args]
        return exclude_list
        """

        return tmp

    exclude = get_channels_obj_from_args(args)

    channels_to_repost = [el for el in channels_to_repost
                          if el not in exclude]

    await show_text_channels(ctx)


@client.command(name="refresh")
async def f(ctx):
    """сбрасывает настройки каналов для репоста до базовых"""
    reset_settings()
    await show_text_channels(ctx)
    print(channels_to_repost)


# endregion

# region for repost and delete ______________________________


@client.command(name="delete")  # remove
async def clear_function(ctx, number_of_messages_to_delete=None):
    n = number_of_messages_to_delete

    if n == "all":
        for message in message_history_list:
            await message.delete()

        await ctx.author.send(f"!delete command was executed for 4 last indexes")

    elif n is None:
        L = last_index = len(message_history_list) - 1

        for index in range(L, L-4, -1):
            await message_history_list[index].delete()

        await ctx.author.send(f"!delete command was executed for 4 last indexes")


# union with on message event and then remove
@client.command(name="repost")
async def repost(ctx):
    """
        репостит сообщение во все каналы из channels_to_repost
        кроме того, в котором была вызвана эта команда !repost...

        (что бы не присылать мем на сервер с которого его стырил)
    """

    message = ctx.message

    if trusted_author(message):
        c = 0
        for channel_id in channels_to_repost:

            this_channel = message.channel
            channel = client.get_channel(channel_id)
            #channel = client.get_channel(991335084986744932)
            if this_channel == channel:
                pass
            else:
                try:
                    msg = await channel.send(message.content)
                    #msg = await channel.send(f"tmp meaasge count = {c}")
                    message_history_list.append(msg)
                    c += 1
                except:
                    pass

        await respond_to_author_of_message(message, response=f"message reposted to {c} "
                                                             f"channels by !repost command")

    else:
        await respond_to_message(message, response=f'Вашего ID нет в моём списке '
                                           f'допущенных к щитпостингу')


@client.event
async def on_message(message):
    """
        репостит сообщение во все каналы из channels_to_repost

        риаботает, когда польлзователь из trusted_users
        отправляет DM (приватное сообщение) боту

        удобно тем что не нужно писать никакую комманду,
        бот сразу репостит мемы
    """

    if message.author == client.user:  # что бы бот не общался сам с собой
        return

    if is_ZUM(message):  # немного заслуженого троллинга
        await bully_ZUM(message)
        return

    # сообщение было написано боту в личку
    is_DM = (message.channel.type == discord.enums.ChannelType.private)

    if trusted_author(message) and is_DM:

        await respond_to_message(message, response=f"через 10 секунд будет репост")
        await asyncio.sleep(10)
        c = 0

        for channel_id in channels_to_repost:

            channel = client.get_channel(channel_id)
            # channel = client.get_channel(991335084986744932)

            try:  # пеерсылаем сообщение, поднимем счётчик пересланых сообщений
                await channel.send(message.content)
                c += 1
            except:
                await respond_with_error(message, channel, channel_id)

        await respond_to_message(message, response=f'message reposted to {c} channels')

    elif (not trusted_author and is_DM):
        await respond_to_message(message, response=f'Вашего ID нет в моём списке '
                                     f'допущенных к щитпостингу' )

    # передать сообщение парсеру комманд, иначе on_message()
    # имеет приоритет выше любого сообщения (в том числе с любой командой)
    await client.process_commands(message)

# endregion

# endregion

# region вспомогательные методы


def exclude_channel(index):
    """убирает из channels_to_repost канал с выбраным индексом"""
    removed_channel = channels_to_repost.pop(index)


async def show_text_channels(message):
    """выводит список доступных каналов для репоста"""


    for i in range(len(channels_to_repost)):

        channel = client.get_channel(channels_to_repost[i])
        channel_name = channel.name

        guild = channel.guild

        response = f"_{i}_: {str(guild)}, {channel_name}"

        await respond_to_message(message, response)


def reset_settings():
    """
    восстанавливаем настройки из settings.txt

    - список каналов для репоста
    - список юзеов, которые могут репостить
    - токен нашего бота

    использовать после init_my_file_parser()
    """

    global trusted_users
    global channels_to_repost
    global token

    token, trusted_users, channels_to_repost = fp.get_attributes()


def init_my_file_parser():
    """
    читаем настройик из settings.txt
    вызывать ___строго___ один раз
    """

    global trusted_users
    global channels_to_repost
    global token

    fp.parse_settings_file()
    token, trusted_users, channels_to_repost = fp.get_attributes()


def trusted_author(message):
    """проверяем, находится ли отправитель _message_ в trusted_users"""

    author = message.author.id

    if author in trusted_users:
        return True
    else:
        return False


async def respond_to_message(message, response):
    """отправляет сообщение {response} в канал где находится {message}"""
    await message.channel.send(response)


async def respond_to_author_of_message(message, response):
    await message.author.send(response)


async def respond_with_error(message, channel, channel_id):
    # просто упаковка большого и бесполезного кода в отдельную функцию

    try:
        await respond_to_message(message, response=f"Error: can't send to: "
                                           f"'{channel.guild}   --->   {channel}' channel")
    except:
        await respond_to_message(message, response=f"Error: can't send to: "
                                           f"'{channel}' channel with id = {channel_id}")


def is_ZUM(message):
    # ZUM from GAYBAR guild 270184210944229381
    # SRONGLAV from GAYBAR guild 982698692740001792
    if message.author.id == 982698692740001792:
        return True
    else:
        return False


async def bully_ZUM(message):
    if random.random() < 0.064:
        await respond_to_message(message, response=f"Сронглав - лошара, опять опозорился")


# endregion

# region настройка и запуск бота

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

init_my_file_parser()
client.run(token)

# endregion
