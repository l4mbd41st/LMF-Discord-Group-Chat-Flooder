import aiosonic
import aiohttp
import asyncio
import random
from pick import pick
from colors import *
import os

def __headers__(token:str, bot=False) -> set:
    if not bot: return {"Authorization": token}
    return {"Authorization": "Bot "+token}

def __tokens__() -> list:
    return open("tokens.txt", "r").read().splitlines()

async def __create_gc_(amount, queue) -> int:
    token = queue.get_nowait()
    try:
        while True:
            if token[1]==amount: queue.task_done()
            async with aiohttp.ClientSession() as session:
                y = await session.post("https://discord.com/api/v9/users/@me/channels", headers={"Authorization": token[0][0], "content-type":"application/json"}, json={"recipients": []})
                json_ = await y.json()
                if y.status in [200, 201, 204]:
                    print("[%s+%s] %sCreated%s GC | %s%s%s" % (green(), reset(), green(), reset(), magenta(), token[1], reset()))
                    queue.put_nowait([token[0][0], token[1]+1])
                elif y.status == 429:
                    print("[%s-%s] %sRate limited%s.. | %s" % (red(), reset(), red(), reset(), json_['retry_after']))
                    await asyncio.sleep(json_['retry_after'])
                    queue.put_nowait(token)
                else:
                    print(json_)
                    return 0x1
    except Exception as e:
        if isinstance(e, asyncio.QueueEmpty):
            await session.close()
            return

async def add_gc_worker(victim:str, queue) -> int:
    gc = queue.get_nowait()
    try:
        while True:
            async with aiohttp.ClientSession() as session:
                x = await session.put("https://discord.com/api/v9/channels/%s/recipients/%s" % (gc[0], victim), headers={"Authorization": gc[1], "content-type":"application/json"}, json={})
                if x.status in [200, 201, 204]:
                    print("[%s+%s] %sAdded to%s %s" % (green(), reset(), green(), reset(), gc[0]))
                    queue.task_done()
                elif x.status == 429:
                    json_ = await x.json()
                    print("[%s-%s] %sRate limited%s.." % (red(), reset(), red(), reset()))
                    await asyncio.sleep(json_['retry_after'])
                    queue.put_nowait(gc)
                else:
                    print(x.status)
                    break
    except Exception as e:
        if isinstance(e, asyncio.QueueEmpty):
            await x.close()
            return

async def __accept_friend(t, vi) -> bool:
    x = await aiosonic.HTTPClient().get("https://discord.com/api/v9/users/@me/relationships", headers=__headers__(t[0], bot=False))
    if x.status_code in [200, 201, 204]:
        for i in await x.json():
            if vi == i['id'] and str(i['type'])=="3":
                print("\n [%s?%s] %sIncoming%s Friend Request | %s" % (blue(), reset(), green(), reset(), t[1]))
                return
            elif vi == i['id'] and str(i['type'])=="1":
                print("\n [%s+%s] Already %sAccepted%s | %s" % (green(), reset(), red(), reset(), t[1]))
                return
        print("\n [%s-%s] Not %sfound%s | %s" % (red(), reset(), red(), reset(), t[1]))
        return
    #if await __get_friends__(t, vi) == False:
        #async with aiohttp.ClientSession() as session:
            #x = await session.put("https://discord.com/api/v9/users/@me/relationships/%s" % vi, json={}, headers={"Authorization":t[0], "content-type":"application/json", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"})
        #if x.status_code in [200, 201, 204]:
            #print(await x.json())

async def __get_friends__(t, vi) -> bool:
    x = await aiosonic.HTTPClient().get("https://discord.com/api/v9/users/@me/relationships", headers=__headers__(t[0], bot=False))
    if x.status_code in [200, 201, 204]:
        if vi in [i['id'] for i in await x.json()]:
            return True
        else:
            return False
    else:
        return False

async def __kick_gc__(gc_id:str, mem:str, token:str) -> bool:
    while True:
        session = await aiosonic.HTTPClient().delete("https://discord.com/api/v9/channels/%s/recipients/%s" % (gc_id, mem), headers={"Authorization": token, "content-type":"application/json"})
        json_ = await session.json()
        if session.status_code != 429:
            return True
        else:
            await asyncio.sleep(json_['retry_after'])

async def __fetch__gcs(token:str, id:str) -> list:
    gcs = []
    session = await aiosonic.HTTPClient().get("https://discord.com/api/v9/users/@me/channels", headers=__headers__(token))
    json_ = await session.json()
    for i in json_:
        try:
            ow = i['owner_id']
            if len(i['recipients'])==0x09:
                if id == ow:
                    try:
                        if await __kick_gc__(i['id'], random.choice([uefi['id'] for uefi in i['recipients']]), token) == True:
                            gcs.append([i['id'], token])
                    except AssertionError:
                        gcs.append([i['id'], token])
            else:
                gcs.append([i['id'], token])
        except KeyError:
            continue
    return gcs

async def load_tokens() -> list:
    z = []
    for t in __tokens__():
        x = await aiosonic.HTTPClient().get(f"https://discord.com/api/v9/users/@me", headers=__headers__(t))
        y = await x.json()
        try:
            z.append([t, y['id']])
        except KeyError:
            continue
    if z==[]:
        return None
    return z

def call() -> int:
    return 0x0

async def farm_gcs(amount:int) -> int:
    queue = asyncio.Queue()
    tasks = []
    for token in token_list:
        queue.put_nowait([token, 0])
    for void_linux in range(0x0, 0x80):
        tasks.append(asyncio.create_task(__create_gc_(amount, queue)))
    await queue.join()
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks)
    return 0x0

async def start_attack(victim:str) -> int:
    total_gcs = []
    for i in token_list:
        for i in await __fetch__gcs(i[0], i[1]):
            total_gcs.append(i)
    for ___ in token_list:
        if await __get_friends__(___, victim) == False:
            print("\n   [%s!%s] '%s%s%s' isn't friended with the %starget%s!" % (blue(), reset(), green(), ___[1], reset(), red(), reset()))
            return 0x1
    queue = asyncio.Queue()
    tasks = []
    for gc in total_gcs:
        queue.put_nowait(gc)
    for FRARAGA in range(0x0, 0xFF):
        tasks.append(asyncio.create_task(add_gc_worker(victim, queue)))
    await queue.join()
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks)
    return 0x0

async def spam_gcs(message:str) -> int:
    total_gcs = []
    for token in token_list:
        gcs = await __fetch__gcs(token[0], token[1])
        total_gcs.extend(gcs)
    queue = asyncio.Queue()
    tasks = []
    for gc in total_gcs:
        queue.put_nowait(gc)
    for _ in range(0x0, 0xFF):
        tasks.append(asyncio.create_task(spam_gc_worker(message, queue)))
    await queue.join()
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks)
    return 0x0

async def spam_gc_worker(message:str, queue) -> int:
    gc = queue.get_nowait()
    try:
        while True:
            async with aiohttp.ClientSession() as session:
                x = await session.post(f"https://discord.com/api/v9/channels/{gc[0]}/messages", headers={"Authorization": gc[1], "content-type":"application/json"}, json={"content": message})
                if x.status in [200, 201, 204]:
                    print("[%s+%s] %sSpammed%s %s" % (green(), reset(), green(), reset(), gc[0]))
                    queue.task_done()
                elif x.status == 429:
                    json_ = await x.json()
                    print("[%s-%s] %sRate limited%s.." % (red(), reset(), red(), reset()))
                    await asyncio.sleep(json_['retry_after'])
                    queue.put_nowait(gc)
                else:
                    print(x.status)
                    break
    except Exception as e:
        if isinstance(e, asyncio.QueueEmpty):
            await x.close()
            return

async def main() -> int:
    print("""



                ▄█         ▄▄▄▄███▄▄▄▄      ▄████████ 
                ███       ▄██▀▀▀███▀▀▀██▄   ███    ███ 
                ███       ███   ███   ███   ███    █▀  
                ███       ███   ███   ███  ▄███▄▄▄     
                ███       ███   ███   ███ ▀▀███▀▀▀     
                ███       ███   ███   ███   ███        
                ███▌    ▄ ███   ███   ███   ███        
                █████▄▄██  ▀█   ███   █▀    ███        
                ▀                                    


        - Good %strolling%s, by %sTakaso%s

""" % (green(), reset(), blue(), reset()))
    input("   [%s+%s] Press %sAnything%s To Start > " % (green(), reset(), magenta(), reset()))
    option, index = pick(["  [ GC Farm ]", "  [ Attack ]", "  [ Friend Checker ]", "  [ Spam GCs ]", "  [ Exit ]"], """



   ________                                                        __  _           
  / ____/ /_  ____  ____  ________     ____ _____     ____  ____  / /_(_)___  ____ 
 / /   / __ \/ __ \/ __ \/ ___/ _ \   / __ `/ __ \   / __ \/ __ \/ __/ / __ \/ __ \\
/ /___/ / / / /_/ / /_/ (__  )  __/  / /_/ / / / /  / /_/ / /_/ / /_/ / /_/ / / / /
\____/_/ /_/\____/\____/____/\___/   \__,_/_/ /_/   \____/ .___/\__/_/\____/_/ /_/ 
                                                        /_/                        
""", indicator=">")
    global token_list
    token_list = await load_tokens()
    # index is unused lol
    match option:
        case "  [ GC Farm ]":
            am = input("   [%s+%s] %sWorkers Amount%s > " % (green(), reset(), magenta(), reset()))
            if am.isnumeric():
                await farm_gcs(int(am))
            else:
                os.system("cls" if os.name == "nt" else "clear")
                return await main()
        case "  [ Attack ]":
            vc:str = str(input("   [%s+%s] %sUser ID%s > " % (green(), reset(), magenta(), reset())))
            if vc.isnumeric():
                await start_attack(vc)
            else:
                os.system("cls" if os.name == "nt" else "clear")
                return await main()
        case "  [ Friend Checker ]":
            vc:str = str(input("   [%s+%s] %sUser ID%s > " % (green(), reset(), magenta(), reset())))
            if vc.isnumeric():
                for _t in token_list:
                    await __accept_friend(_t, vc)
            input()
            os.system("cls" if os.name == "nt" else "clear")
            return await main()
        case "  [ Spam GCs ]":
            message = input("   [%s+%s] %sMessage to Spam%s > " % (green(), reset(), magenta(), reset()))
            await spam_gcs(message)
            os.system("cls" if os.name == "nt" else "clear")
            return await main()
        case "  [ Exit ]":
            exit(0x0)
    return 0x0

asyncio.run(main())

input()
