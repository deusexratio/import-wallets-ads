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
    time.sleep(1)
    # Клик на "Import Secret Recovery Phrase"
    # wallet_page.locator("//button[text()='I already have a wallet']").click()
    wallet_page.locator("//*[@id='root']/main/div[2]/div/div[2]/button[2]").click()
    time.sleep(1)

    # Клик на "Import an existing wallet"
    # wallet_page.locator("//div[text()='Import Secret Recovery Phrase']").click()
    wallet_page.locator("//*[@id='root']/main/div[2]/div/div[2]/button[1]").click()
    time.sleep(1)

    # Вводим seed
    wallet_page.get_by_test_id(test_id='secret-recovery-phrase-word-input-0').press_sequentially(seed)
    time.sleep(1)

    # Import Wallet
    wallet_page.get_by_test_id(test_id='onboarding-form-submit-button').click()
    time.sleep(5)

    # Import Wallet
    wallet_page.get_by_test_id(test_id='onboarding-form-submit-button').click()
    time.sleep(1)

    # Вводим пароль
    wallet_page.get_by_test_id(test_id='onboarding-form-password-input').fill(password)
    wallet_page.get_by_test_id(test_id='onboarding-form-confirm-password-input').fill(password)
    time.sleep(1)

    # Ставим галочку
    try:
        checkbox = wallet_page.locator('//input[@type="checkbox"]')
        checkbox.check()
    except Error:
        print('Enabled checkbox')

    # checked = expect(
    # wallet_page.get_by_test_id(test_id='onboarding-form-terms-of-service-checkbox')).to_be_attached(timeout=1000)
    # print(checked)
    # if not checked:
    #     wallet_page.get_by_test_id(test_id='onboarding-form-terms-of-service-checkbox').click()
    # except:
    #     wallet_page.get_by_test_id(test_id='onboarding-form-terms-of-service-checkbox').click()
    #     time.sleep(.5)

    # Нажимаем кнопку "Импортировать"
    wallet_page.get_by_test_id(test_id='onboarding-form-submit-button').click()
    time.sleep(1)

    # Завершаем процесс импорта
    wallet_page.get_by_test_id(test_id='onboarding-form-submit-button').click()
    time.sleep(1)
    wallet_page.close()

    # cprint(text=f'Success {ads_id}', color='green')


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
            browser = p.chromium.connect_over_cdp(resp["data"]["ws"]["puppeteer"])
            url = 'chrome-extension://bfnaelmomeimhlpmgjnjophhpkkoljpa/onboarding.html'

            context = browser.contexts[0]
            wallet_page = context.new_page()
            wallet_page.bring_to_front()
            wallet_page.set_viewport_size({"width": 500, "height": 700})
            time.sleep(7)
            wallet_page.goto(url)
            time.sleep(2)

            try:
                onboard_page(wallet_page, seed, password)
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

    line_control("id_users.txt")
    line_control("seeds.txt")

    with open("id_users.txt", "r") as f:
        id_users = [row.strip() for row in f]

    with open("seeds.txt", "r") as f:
        seeds = [row.strip() for row in f]

    # Set your password
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
