import asyncio
import time
import os
from dotenv import load_dotenv

from playwright.async_api import async_playwright
from capmonstercloudclient import CapMonsterClient, ClientOptions
from capmonstercloudclient.requests import RecaptchaV2Request

# Fornecedores de CAPTCHA
# https://capmonster.cloud/
# https://pypi.org/project/capmonstercloudclient/
# https://github.com/ZennoLab/capmonstercloud-client-python/blob/main/examples/recaptchaV2.py
# https://github.com/ZennoLab/capmonstercloud-client-python/tree/main
# https://docs.capsolver.com/en/
# https://brightdata.com/products/web-unlocker

load_dotenv()

# CapMonster API Key    
CAP_MONSTER_API_KEY = os.getenv("CAP_MONSTER_API_KEY")

client_options = ClientOptions(api_key=CAP_MONSTER_API_KEY)
cap_monster_client = CapMonsterClient(options=client_options)

recaptcha2request = RecaptchaV2Request(websiteUrl="https://www2.trf4.jus.br/trf4/processos/certidao/index.php",
                                                websiteKey="6Ldv-vIUAAAAAN2v6GbNs9w5HTS0HTTLhFL8dDB8")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        # Create a new page in the provided browser context
        page = await context.new_page()

        # Navigate to the hCaptcha test page using a predefined site key
        await page.goto('https://www2.trf4.jus.br/trf4/processos/certidao/index.php')

        await page.fill('//*[@id="string_cpf"]', '10043770614')

        responses = await solve_captcha()
        response = responses['gRecaptchaResponse']
        
        await page.eval_on_selector('#g-recaptcha-response', '(el) => el.value =' +"'"+ response +"'")
        await page.click('//*[@id="frmCertidao"]/fieldset/b/input[1]')
        
        time.sleep(10)

        await page.click('//*[@id="botaoEmitir"]')

        time.sleep(10)

async def solve_captcha():
    return await cap_monster_client.solve_captcha(recaptcha2request)

if __name__ == "__main__":
    asyncio.run(main())
