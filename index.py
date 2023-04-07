# importando bibliotecas
import pandas as pd
import datetime
import yfinance as yf
from matplotlib import pyplot as plt
import mplcyberpunk
import smtplib
from email.message import EmailMessage

import os
from dotenv import load_dotenv

load_dotenv()

# pegando dados do yahoo finance
actives = ["^BVSP", "BRL=X"]

today = datetime.datetime.now()
last_year = today - datetime.timedelta(days=365)

data = yf.download(actives, last_year, today)


# manipulando dados
data_closing = data["Adj Close"]
data_closing.columns = ['dolar', 'ibovespa']

data_closing = data_closing.dropna()


# criando tabelas com outros timeframes
data_closing_monthly = data_closing.resample('M').last()
data_closing_annual = data_closing.resample('Y').last()


# calcular closing do dia, retorno no ano e retorno no mês
return_daily = data_closing.pct_change().dropna()
return_monthly = data_closing_monthly.pct_change().dropna()
return_annual = data_closing_annual.pct_change().dropna()


# localizar o closing do dia anterior, retorno do mês e retorno no ano
return_day_dolar = round(return_daily.iloc[-1, 0] * 100, 2)
return_day_ibov = round(return_daily.iloc[-1, 1] * 100, 2)

return_month_dolar = round(return_monthly.iloc[-1, 0] * 100, 2)
return_month_ibov = round(return_monthly.iloc[-1, 1] * 100, 2)

return_year_dolar = round(return_annual.iloc[-1, 0] * 100, 2)
return_year_ibov = round(return_annual.iloc[-1, 1] * 100, 2)


# plotar gráficos de performance
plt.style.use("cyberpunk")

data_closing.plot(y='dolar', use_index=True, legend=False)

plt.title("Dolar")

plt.savefig("dolar.png", dpi=300)

plt.show()

data_closing.plot(y='ibovespa', use_index=True, legend=False)

plt.title("Ibovespa")

plt.savefig("ibovespa.png", dpi=300)

plt.show()


# enviar email com relatórios
name = os.environ.get("name")
password = os.environ.get("password_email")
email = os.environ.get("email")

msg = EmailMessage()
msg['Subject'] = "Relatório de fechamento Ibovespa e Dólar"
msg['From'] = email
msg['To'] = email

msg.set_content(f'''Prezado diretor, segue o relatório diário:

Bolsa:

No ano o Ibovespa está tendo uma rentabilidade de {return_year_ibov}%, 
enquanto no mês a rentabilidade é de {return_month_ibov}%.

No último dia útil, o closing do Ibovespa foi de {return_day_ibov}%.

Dólar:

No ano o Dólar está tendo uma rentabilidade de {return_year_dolar}%, 
enquanto no mês a rentabilidade é de {return_month_dolar}%.

No último dia útil, o closing do Dólar foi de {return_day_dolar}%.


At.te,

{name}

''')

with open('dolar.png', 'rb') as content_file:
    content = content_file.read()
    msg.add_attachment(content, maintype='application',
                       subtype='png', filename='dolar.png')


with open('ibovespa.png', 'rb') as content_file:
    content = content_file.read()
    msg.add_attachment(content, maintype='application',
                       subtype='png', filename='ibovespa.png')

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:

    smtp.login(email, password)
    smtp.send_message(msg)
