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


def onboard_page(wallet_page, private_key, password, ads_id):
    # time.sleep(30)
    # Клик на "Import Secret Recovery Phrase"
    # wallet_page.locator("//button[text()='I already have a wallet']").click()
    wallet_page.locator("//*[@id='root']/main/div[2]/div/div[2]/button[2]").click()
    time.sleep(1)

    # Клик на "Import an existing wallet"
    # wallet_page.locator("//div[text()='Import Secret Recovery Phrase']").click()
    wallet_page.locator("//*[@id='root']/main/div[2]/div/div[2]/button[2]").click()
    time.sleep(1)

    # Вводим private key
    wallet_page.get_by_placeholder('Name').fill(ads_id)
    wallet_page.get_by_placeholder('Private key').fill(private_key)
    time.sleep(1)

    # Import Wallet
    wallet_page.get_by_test_id(test_id='onboarding-form-submit-button').click()
    time.sleep(1)

    # Вводим пароль
    wallet_page.get_by_test_id(test_id='onboarding-form-password-input').fill(password)
    wallet_page.get_by_test_id(test_id='onboarding-form-confirm-password-input').fill(password)
    # time.sleep(.5)

    # Ставим галочку
    try:
        checkbox = wallet_page.locator('//input[@type="checkbox"]')
        checkbox.check()
    except Error:
        print('checkbox was already checked')
    time.sleep(.5)

    # Нажимаем кнопку "Импортировать"
    wallet_page.get_by_test_id(test_id='onboarding-form-submit-button').click()
    time.sleep(1)

    # Завершаем процесс импорта
    wallet_page.get_by_test_id(test_id='onboarding-form-submit-button').click()
    time.sleep(1)

    # cprint(text=f'Success {ads_id}', color='green')


def main(zero, ads_id, private_key, password):
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
            browser = p.chromium.connect_over_cdp(resp["data"]["ws"]["puppeteer"])
            url = 'chrome-extension://bfnaelmomeimhlpmgjnjophhpkkoljpa/onboarding.html'

            context = browser.contexts[0]
            wallet_page = context.new_page()
            wallet_page.bring_to_front()
            time.sleep(2)
            wallet_page.goto(url)
            time.sleep(2)

            try:
                onboard_page(wallet_page, private_key, password, ads_id)
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

    line_control("private_keys.txt")
    line_control("id_users_private_keys.txt")

    with open("id_users_private_keys.txt", "r") as f:
        id_users = [row.strip() for row in f]

    with open("private_keys.txt", "r") as f:
        private_keys = [row.strip() for row in f]

        # Set your password
    password = '12345678'

    for i, ads_id in enumerate(id_users):
        try:
            main(i, ads_id, private_keys[i], password)
            time.sleep(5)
        except IndexError as ex:
            cprint(f'\nCheck the correspondence of the number of seed phrases with '
                   f'the number of profiles in the files id_users.txt and seeds.txt', 'red')
            sys.exit(0)
        except Exception as ex:
            cprint(str(ex), 'red')
