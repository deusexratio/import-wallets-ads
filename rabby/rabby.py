import asyncio

import requests, time, sys
from playwright.async_api import async_playwright, expect
from playwright._impl._errors import TimeoutError, Error, TargetClosedError
from termcolor import cprint
import traceback

def line_control(file_txt):
    # Удаление пустых строк
    with open(file_txt) as f1:
        lines = f1.readlines()
        non_empty_lines = (line for line in lines if not line.isspace())
        with open(file_txt, "w") as n_f1:
            n_f1.writelines(non_empty_lines)


async def onboard_page(rabby_page, seed, password, context, ads_id):
    await rabby_page.bring_to_front()

    # if await rabby_page.get_by_text('Gwei').is_visible(timeout=3000)

    await rabby_page.get_by_text('I already have an address').click(timeout=3000)

    await rabby_page.get_by_text('Seed Phrase').click(timeout=3000)

    await rabby_page.locator('//input').first.fill(seed)

    await asyncio.sleep(1)

    # confirm_button = rabby_page.get_by_text('Confirm')
    confirm_button = rabby_page.locator('//button').last
    await confirm_button.click(timeout=3000)

    await rabby_page.get_by_placeholder("8 characters min").fill(password)
    await rabby_page.get_by_placeholder("Password").fill(password)

    await asyncio.sleep(1)
    try:
        await confirm_button.click(timeout=3000)
    except TargetClosedError:
        print(f"{ads_id} already recovered")

    await rabby_page.get_by_text("Get Started").click(timeout=3000)

    await expect(rabby_page.get_by_text('Rabby Wallet is Ready to Use')).to_be_visible(timeout=5000)
    print(ads_id, 'done')

async def task(zero, ads_id, seed, password, semaphore):
    try:
        async with semaphore:
            args1 = ["--disable-popup-blocking", "--window-position=700,0"]
            args1 = str(args1).replace("'", '"')

            open_url = f"http://local.adspower.net:50325/api/v1/browser/start?user_id=" + ads_id + f"&launch_args={str(args1)}"
            close_url = "http://local.adspower.net:50325/api/v1/browser/stop?user_id=" + ads_id

            try:
                # Отправка запроса на открытие профиля
                resp = requests.get(open_url).json()
                time.sleep(.5)
            except requests.exceptions.ConnectionError:
                cprint(f'Adspower is not running.', 'red')
                sys.exit(0)
            except requests.exceptions.JSONDecodeError:
                cprint(f'Проверьте ваше подключение. Отключите VPN/Proxy используемые напрямую.', 'red')
                sys.exit(0)
            except KeyError:
                resp = requests.get(open_url).json()

            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(resp["data"]["ws"]["puppeteer"])
                url = 'chrome-extension://acmacodkjbdgmoleebolmdjonilkdbch/index.html#/new-user/guide'

                context = browser.contexts[0]
                wallet_page = await context.new_page()
                await wallet_page.bring_to_front()
                await asyncio.sleep(1)
                await wallet_page.goto(url)
                await asyncio.sleep(1)

                try:
                    await onboard_page(wallet_page, seed, password, context, ads_id)
                except TimeoutError as e:
                        print(ads_id, '  fail')
                        requests.get(close_url)
                        return

            requests.get(close_url)
            cprint(f'{zero + 1}. {ads_id} - done', 'green')

    except Exception as ex:
        traceback.print_exc()
        time.sleep(.3)
        cprint(f'{zero + 1}. {ads_id} = error', 'yellow')
        requests.get(close_url)


async def main():
    line_control("id_users.txt")
    line_control("seeds.txt")

    with open("id_users.txt", "r") as f:
        id_users = [row.strip() for row in f]

    with open("seeds.txt", "r") as f:
        seeds = [row.strip() for row in f]

    # Set your password
    password = '12345678'

    # How many threads
    threads = 3

    semaphore = asyncio.Semaphore(threads)
    tasks = [asyncio.create_task(task(i, ads_id, seeds[i], password, semaphore)) for i, ads_id in enumerate(id_users)]

    print(f"Starting {len(tasks)} tasks")
    await asyncio.wait(tasks)


if __name__ == '__main__':
    asyncio.run(main())

