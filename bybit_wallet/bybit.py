import requests, time, sys
# from playwright.async_api import async_playwright, expect
from playwright.sync_api import sync_playwright, expect
from playwright._impl._errors import TimeoutError, Error
from termcolor import cprint
import traceback


def line_control(file_txt):
    # Удаление пустых строк
    with open(file_txt) as f1:
        lines = f1.readlines()
        non_empty_lines = (line for line in lines if not line.isspace())
        with open(file_txt, "w") as n_f1:
            n_f1.writelines(non_empty_lines)


def onboard_page(wallet_page, seed, password):
    try:
        # wallet_page.wait_for_selector("text='Wallet 1'", timeout=5000)

        wallet_page.get_by_text('Import Existing Wallet').click()
        # wallet_page.locator("//*[@id='root']/main/div[2]/div/div[2]/button[2]").click()
        time.sleep(.5)

        wallet_page.get_by_placeholder('Enter your password').first.fill(password)
        wallet_page.get_by_placeholder('Re-enter your password').first.fill(password)

        wallet_page.get_by_text('I agree to ').click()
        time.sleep(.5)

        # wallet_page.get_by_text('Confirm').first.click()
        wallet_page.locator('#__plasmo > footer > button').first.click()
        wallet_page.get_by_text('Import Wallet').first.click()

        # Import Wallet
        seeds_ = seed.split(' ')
        i_ = 1
        for seed in seeds_:
            wallet_page.locator(f'//*[@id="__plasmo"]/main/div[2]/div[1]/div/div[2]/div/div[{i_}]/div/input').fill(seed)
            i_ += 1

        # Finish
        for _ in range(5):
            wallet_page.locator('#__plasmo > main > div.flex-1.flex.flex-col > div:nth-child(2) > button').first.click()
            try:
                wallet_page.wait_for_selector("text='Wallet 1'", timeout=5000)
                if wallet_page.locator("text='Wallet 1'").is_visible():
                    break
            except:
                continue
        else:
            print(ads_id, "не смог завершить импорт")

        wallet_page.close()

        cprint(text=f'Success {ads_id}', color='green')
    except Exception as e:
        print(ads_id, e)
        wallet_page.close()
        return None


def main(zero, ads_id, seed, password):
    try:
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


        with sync_playwright() as p:

            try:
                browser = p.chromium.connect_over_cdp(resp["data"]["ws"]["puppeteer"])
                url = 'chrome-extension://pdliaogehgdbhbnmkklieghmmjkpigpa/popup.html#/start'

                context = browser.contexts[0]
                wallet_page = context.new_page()
                wallet_page.bring_to_front()
                wallet_page.set_viewport_size({"width": 500, "height": 1000})
                time.sleep(5)
                wallet_page.goto(url)
                time.sleep(2)

                onboard_page(wallet_page, seed, password)
            except TimeoutError as e:
                # playwright._impl._errors.TimeoutError: BrowserType.connect_over_cdp: Timeout 30000ms exceeded.
                # это если профиль открылся но плейврайт не смог ничего сделать
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


if __name__ == '__main__':

    line_control("id_users.txt")
    line_control("seeds.txt")

    with open("id_users.txt", "r") as f:
        id_users = [row.strip() for row in f]

    with open("seeds.txt", "r") as f:
        seeds = [row.strip() for row in f]


    password = '12345678'

    for i, ads_id in enumerate(id_users):
        try:
            main(i, ads_id, seeds[i], password)
            time.sleep(5)
        except IndexError as ex:
            cprint(f'\nCheck the correspondence of the number of seed phrases with '
                   f'the number of profiles in the files id_users.txt and seeds.txt', 'red')
            sys.exit(0)
        except Exception as ex:
            cprint(str(ex), 'red')
