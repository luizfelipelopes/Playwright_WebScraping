from playwright.sync_api import sync_playwright
import requests
import time

CAPMONSTER_API_KEY = "67fbd9db80962c1991f75429d7bb864f"
TSE_URL = "https://filia2-consulta.tse.jus.br/#/principal/menu"

## IMPORTANT ##
## fill the dictionary below with your details ##
proxies = {
  "server": "brd.superproxy.io:33335",
  "username": 'brd-customer-hl_7808018b-zone-luiz_zone',
  "password": 'c3tptkr019ll'
}


def get_hcaptcha_solution(website_url, website_key):
    print("🧠 Enviando CAPTCHA para CapMonster...")

    try:

      task_payload = {
          "clientKey": CAPMONSTER_API_KEY,
          "task": {
              "type": "HCaptchaTaskProxyless",
              "websiteURL": website_url,
              "websiteKey": website_key
          }
      }

      create_task = requests.post("https://api.capmonster.cloud/createTask", json=task_payload).json()
      task_id = create_task.get("taskId")
      # if not task_id:
      #     raise Exception("❌ Falha ao criar tarefa no CapMonster")

      # Loop de verificação
      result_payload = {
          "clientKey": CAPMONSTER_API_KEY,
          "taskId": task_id
      }

      for _ in range(30):  # tenta por até ~30s
          time.sleep(5)
          result = requests.post("https://api.capmonster.cloud/getTaskResult", json=result_payload).json()
          if result.get("status") == "ready":
              print("✅ hCaptcha resolvido com sucesso!")
              return result["solution"]["gRecaptchaResponse"]
      
      # raise Exception("⏳ Timeout na resolução do hCaptcha")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")

# initiallize playwright
# pw = sync_playwright().start()

with sync_playwright() as pw:

  # create Firefox browser object
  browser = pw.firefox.launch(
      # uncomment the lines below if you're using a web driver
      headless=False, 
      slow_mo=10000,
      proxy=proxies
  )


  context = browser.new_context(ignore_https_errors=True)
  page = context.new_page()

  # create new browser tab
  # page = browser.new_page()
  # navigate to web page locked by CAPTCHA
  # page.goto("http://www.walmart.com")
  
  
  page.goto(TSE_URL, wait_until="networkidle")
  print("🌐 Acessando página da TSE...")

  # Aguarda a interface carregar (Angular)
  page.wait_for_selector("mat-card-title", timeout=10000)

  # Clica no menu "Certidão de filiação partidária"
  # page.click('//html/body/app-root/div/app-principal/mat-sidenav-container/mat-sidenav-content/app-menu/div/mat-grid-list/div/mat-card/mat-card-header/div/mat-card-title/mat-nav-list/a')
  # page.click('//html/body/app-root/div/app-principal/mat-sidenav-container/mat-sidenav-content/app-sub-menu-certidao/div/div/mat-card/mat-card-header/div/mat-card-title/mat-nav-list/a[1]')

  # Verifica se há iframe de reCAPTCHA (opcional)
  if page.query_selector("iframe[src*='recaptcha']"):
      print("⚠️ CAPTCHA detectado na página")
  else:
      print("✅ Nenhum CAPTCHA visível detectado")

# https://newassets.hcaptcha.com/captcha/v1/5f35773783128732d39973502d72d1c1bb8dfc55/static/hcaptcha.html#frame=checkbox
# &id=0lq6zw3gyj5
# &host=filia2-consulta.tse.jus.br
# &sentry=true
# &reportapi=https%3A%2F%2Faccounts.hcaptcha.com
# &recaptchacompat=true
# &custom=false
# &hl=pt-BR
# &tplinks=on
# &pstissuer=https%3A%2F%2Fpst-issuer.hcaptcha.com
# &sitekey=b70aa17e-b288-4562-9a6c-100007da8f4a
# &theme=light&origin=https%3A%2F%2Ffilia2-consulta.tse.jus.br


  # Aguarda a renderização do hCaptcha e obtém o sitekey
  print("🔍 Buscando sitekey do hCaptcha...")
  # captcha_elem = page.wait_for_selector("div[data-sitekey]", timeout=10000)
  # sitekey = captcha_elem.get_attribute("data-sitekey")
  sitekey = 'b70aa17e-b288-4562-9a6c-100007da8f4a'

  # Solicita solução ao CapMonster
  token = get_hcaptcha_solution(TSE_URL, sitekey)

  print("🧩 Token do hCaptcha obtido!")
  print(f"🔑 Token: {token}")

  # Injeta o token no campo oculto do hCaptcha
  print("🧬 Injetando token na página...")
  page.evaluate("""
      (token) => {
          let textarea = document.querySelector('textarea[name="h-captcha-response"]');
          if (!textarea) {
              textarea = document.createElement("textarea");
              textarea.name = "h-captcha-response";
              textarea.style.display = "none";
              document.body.appendChild(textarea);
          }
          textarea.value = token;
          textarea.dispatchEvent(new Event('input', { bubbles: true }));
      }
  """, token)

  # Marca o checkbox visualmente, se necessário (opcional)
    # page.click('iframe[src*="hcaptcha"]')

  print("🟢 Token injetado! Agora o botão deve ser habilitado.")


  
  # page.goto("https://www.tse.jus.br/servicos-eleitorais/certidoes/certidao-de-filiacao-partidaria")
  # frame = page.frame(url="https://filia2-consulta.tse.jus.br/#/principal/menu")

  # page.click('//html/body/app-root/div/app-principal/mat-sidenav-container/mat-sidenav-content/app-menu/div/mat-grid-list/div/mat-card/mat-card-header/div/mat-card-title/mat-nav-list/a')
  # page.click('//html/body/app-root/div/app-principal/mat-sidenav-container/mat-sidenav-content/app-sub-menu-certidao/div/div/mat-card/mat-card-header/div/mat-card-title/mat-nav-list/a[1]')

  # page.fill('//*[@id="mat-input-0"]', '165014040213')
  # page.fill('//*[@id="mat-input-1"]', 'Luiz Felipe Cordiro Lopes')
  # page.fill('//*[@id="mat-input-3"]', 'Maria Fernanda Cordeiro Lopes')
  # page.fill('//*[@id="mat-input-4"]', 'João Izabel Lopes')

  # page.fill('//*[@id="mat-input-2"]', '08/01/1990')
  # page.click('//*[@id="mat-datepicker-0"]/div/mat-month-view/table/tbody/tr[1]/td[4]/button')
  # page.eval_on_selector('//*[@id="mat-input-2"]', f"""
  #                       el => {{
  #                             el.value = '08/01/1990';
  #                             el.dispatchEvent(new Event('input', {{ bubbles: true }}));
  #                         }}""")
  # page.click('//html/body/app-root/div/app-principal/mat-sidenav-container/mat-sidenav-content/app-gerar-certidao/section/div/article/form')
  
  # page.click('//html/body/app-root/div/app-principal/mat-sidenav-container/mat-sidenav-content/app-gerar-certidao/section/div/article/form/mat-card/mat-card-content/div[6]/button[3]')





  # # locate search input
  # page.locator("xpath=//input[@aria-label='Search']").fill("testing")
  # # submit search term
  # page.keyboard.press('Enter');

  browser.close()
