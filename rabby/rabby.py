import requests, time, sys
# from playwright.async_api import async_playwright, expect
from playwright.sync_api import sync_playwright, expect
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


def onboard_page(wallet_page, seed, password, context, ads_id):
    time.sleep(1)
    try:
        expect(wallet_page.locator('//button[@type="button"]'))
    except Error:
        wallet_page.close()
        print(ads_id, '   fail at first page')
        return

    password_field = wallet_page.get_by_placeholder("Enter the Password to Unlock")
    if password_field.is_visible():
        password_field.fill(password)
        wallet_page.locator('//button[@type="submit"]').click()
        time.sleep(.5)
        if wallet_page.get_by_text('Seed Phrase 1').first.is_visible():
            wallet_page.close()
            print(ads_id, '  already done')
            return

        # Клик на "Import Seed Phrase" Import Seed Phrase //*[@id="root"]/div/div[3]/div[2]/div[1]/div
        with context.expect_page() as new_wallet_page_info:
            wallet_page.locator("//div[text()='Import Seed Phrase']").click()
        time.sleep(.5)
        new_wallet_page = new_wallet_page_info.value

        new_wallet_page.locator('//input[@type="password"]').first.fill(seed)
        time.sleep(.5)
        new_wallet_page.get_by_text('Confirm').click()
            # //button[@type='submit']

        new_wallet_page.locator(
                '//*[@id="rc-tabs-0-panel-hd"]/div/div/div/div/div/div[2]/table/tbody/tr[2]/td[1]/button').click()
        time.sleep(.5)
        new_wallet_page.get_by_text('Done').click()

    else:
        # Клик на "Next"
        wallet_page.locator('//button[@type="button"]').click()
        time.sleep(.5)

        # Клик на "Get started"
        wallet_page.locator('//button[@type="button"]').click()
        time.sleep(.5)

        # Клик на "Import Seed Phrase" Import Seed Phrase //*[@id="root"]/div/div[3]/div[2]/div[1]/div
        wallet_page.locator("//div[text()='Import Seed Phrase']").click()
        time.sleep(.5)

        # Вводим password
        wallet_page.get_by_placeholder('Password must be at least 8 characters long').fill(password)
        wallet_page.get_by_placeholder('Confirm password').fill(password)
        time.sleep(.5)

        # Клик на "Import Seed Phrase" Import Seed Phrase //*[@id="root"]/div/div[3]/div[2]/div[1]/div
        with context.expect_page() as new_wallet_page_info:
            wallet_page.get_by_text('Next').click() # //*[@id="root"]/div/div/div/form/div[3]/button # //button[@type='submit']
        new_wallet_page = new_wallet_page_info.value

        # Enter seed
        # wallet_page.locator("//input[@type='password']").fill(seed)
        new_wallet_page.locator('//input[@type="password"]').first.fill(seed)
        time.sleep(.5)
        new_wallet_page.get_by_text('Confirm').click()
        # //button[@type='submit']

        # new_wallet_page.locator(
        #     '//*[@id="rc-tabs-0-panel-hd"]/div/div/div/div/div/div[2]/table/tbody/tr[2]/td[1]/button').click()
        # new_wallet_page.locator('//button[@role="switch"]').first.click()
        new_wallet_page.get_by_role('switch').first.click()
        time.sleep(1.5)
        new_wallet_page.get_by_text('Done').click()
        # //*[@id="root"]/div/div/button
        new_wallet_page.close()

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
        except KeyError:
            resp = requests.get(open_url).json()

        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(resp["data"]["ws"]["puppeteer"])
            url = 'chrome-extension://acmacodkjbdgmoleebolmdjonilkdbch/index.html'

            context = browser.contexts[0]
            wallet_page = context.new_page()
            wallet_page.bring_to_front()
            time.sleep(1)
            wallet_page.goto(url)
            time.sleep(1)

            try:
                onboard_page(wallet_page, seed, password, context, ads_id)
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


if __name__ == '__main__':

    line_control("../rabby/id_users.txt")
    line_control("../rabby/seeds.txt")

    with open("id_users_evm.txt", "r") as f:
        id_users = [row.strip() for row in f]

    with open("seeds_evm.txt", "r") as f:
        seeds = [row.strip() for row in f]

    # Set your password
    password = '12345678'

    for i, ads_id in enumerate(id_users):
        try:
            main(i, ads_id, seeds[i], password)
        except IndexError as ex:
            cprint(f'\nCheck the correspondence of the number of seed phrases with '
                   f'the number of profiles in the files id_users.txt and seeds.txt', 'red')
            sys.exit(0)
        except Exception as ex:
            cprint(str(ex), 'red')
