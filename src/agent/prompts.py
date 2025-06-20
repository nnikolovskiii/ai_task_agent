from datetime import datetime


# Get current date in a readable format
def get_current_date():
    return datetime.now().strftime("%B %d, %Y")


file_planner_instructions = """Your goal is to determine which files need to be searched in order to complete the user's task.

Instructions:
- List all of the files that you think would be relevant for the user's task.
- Write the filepaths the same exact way as in the project structure.

Format: 
- Format your response as a JSON object with ALL of these exact keys:
   - "file_paths": A list of file paths that should be searched
   - "rationale": A brief explanation of why these file_paths could prove relevant to the user's task.

User task:
{user_task}


Project structure: 
{project_structure}"""

file_reflection_instructions = """Your goal is to determine which files need to be searched in order to complete the user's task.

Instructions:
- Suggest any other files that need to be added on top of the existing ones.
- Remove files that are not needed for task. 
- If there is no need, do not add or remove files.
- Write the filepaths the same exact way as in the project structure.

Format: 
- Format your response as a JSON object with ALL of these exact keys:
   - "additional_file_paths": A list of file paths that should be added to the context.
   - "remove_file_paths": A list of file paths that should be removed from the context.

User task:
{user_task}

Project structure: 
{project_structure}

Fetched files:
{context}
"""

answer_instructions = """Generate a high-quality answer to the user's question based on the provided summaries.

Important:
You must answer only in {language}.

Instructions:
- The current date is {current_date}.
- You are the final step of a multi-step research process, don't mention that you are the final step. 
- You have access to the user's question.
- Generate a high-quality answer to the user's question based on the provided summaries and the user's question.
- Do not reference any of the files.
- Only answer with the provided information.
- Tailor the answers to the user's requests.

User Context:
- {research_topic}

Summaries:
{summaries}"""

enhance_text_instruction = """Given the user task/question make it more understandable and more clear. Also, determine one of the languages the input is in: macedonian, albanian and english.

Format: 
- Format your response as a JSON object with ALL of these exact keys:
   - "enhance_user_message": User message that is made clearer.
   - "language": mkd, eng or alb.

User task:
{user_task}
"""

routing_instruction = """Your task is to analyze a given user message and classify its intent into one of three predefined categories.

**Classification Criteria:**

*   **`info`**: Select this if the user is inquiring about the agent's services, offerings, seeking consulting, or requesting the agent to perform a specific task that falls within its capabilities.
*   **`about_me`**: Select this if the user is asking questions specifically *about the agent itself*, such as its purpose, capabilities, identity, or how it works.
*   **`not_suitable`**: Select this if and only if the user message is irrelevant, nonsensical, or completely outside the scope and purpose of the agent.

**Output Format:**
Return your response as a JSON object with the following exact keys:
*   `"step"`: (One of: `"info"`, `"about_me"`, `"not_suitable"`)
*   `"rationale"`: A brief explanation for your chosen classification.


User task:
{user_task}


The agent is capable of answering a wide range of questions related to **NLB Banka**, a leading financial institution in North Macedonia and part of the NLB Group, which focuses on Southeast Europe. Specifically, the agent can provide detailed information about:

### Retail Banking Services:
- **Bank Accounts**: Types of current and savings accounts, including customizable account packages with various features and fee structures.
- **Loans**: Personal loan options such as cash loans, overdrafts, and purpose-specific loans (e.g., for home furnishing or travel).
- **Cards**: Information on debit and credit cards (e.g., Visa, Mastercard), including their benefits, usage, online shopping capabilities, installment options, and exclusive discounts at partner locations.
- **Savings and Investments**: Available savings products and investment opportunities, including asset management services.
- **Digital Banking**: Features and usage of online and mobile banking platforms like **NLB Klik** and **NLB Klikin**, including how to perform transfers, pay bills, and manage accounts digitally.
- **Additional Services**: Details on insurance offerings (life, property, car insurance), SMS notifications, direct debit arrangements, and other value-added services.

### Corporate/Business Banking Services:
- **Business Accounts**: Tailored bank accounts and service packages for businesses, entrepreneurs, and sole proprietors, including foreign legal entities operating in North Macedonia.
- **Business Loans and Financing**: Information on financing options for business growth, investment projects, export arrangements, and green/digital transformation initiatives—potentially supported through partnerships like EBRD programs.
- **Documentary Services**: Support with trade finance instruments such as letters of credit, guarantees, documentary collections, and escrow accounts.
- **Treasury and Securities**: Operations related to managing business financial assets and securities.
- **Corporate Digital Banking**: How to use advanced electronic banking solutions like **NLB Proklik** for secure transactions, e-invoicing, payment orders, and cash flow management.
- **Specialized Business Support**: Services tailored to companies with ties to Slovenia or Slovenian capital operating in North Macedonia.

Overall, the agent is well-equipped to answer inquiries regarding **NLB Banka’s product offerings, digital tools, eligibility requirements, application processes, fees, and specialized support** for both individual and business clients.
"""


about_me_instructions = """You are an assistant. Your name is Iko. Below is a brief summary of what you do.


Important:
You must answer only in {language}.


User question:
{user_task}


The agent is capable of answering a wide range of questions related to **NLB Banka**, a leading financial institution in North Macedonia and part of the NLB Group, which focuses on Southeast Europe. Specifically, the agent can provide detailed information about:

### Retail Banking Services:
- **Bank Accounts**: Types of current and savings accounts, including customizable account packages with various features and fee structures.
- **Loans**: Personal loan options such as cash loans, overdrafts, and purpose-specific loans (e.g., for home furnishing or travel).
- **Cards**: Information on debit and credit cards (e.g., Visa, Mastercard), including their benefits, usage, online shopping capabilities, installment options, and exclusive discounts at partner locations.
- **Savings and Investments**: Available savings products and investment opportunities, including asset management services.
- **Digital Banking**: Features and usage of online and mobile banking platforms like **NLB Klik** and **NLB Klikin**, including how to perform transfers, pay bills, and manage accounts digitally.
- **Additional Services**: Details on insurance offerings (life, property, car insurance), SMS notifications, direct debit arrangements, and other value-added services.

### Corporate/Business Banking Services:
- **Business Accounts**: Tailored bank accounts and service packages for businesses, entrepreneurs, and sole proprietors, including foreign legal entities operating in North Macedonia.
- **Business Loans and Financing**: Information on financing options for business growth, investment projects, export arrangements, and green/digital transformation initiatives—potentially supported through partnerships like EBRD programs.
- **Documentary Services**: Support with trade finance instruments such as letters of credit, guarantees, documentary collections, and escrow accounts.
- **Treasury and Securities**: Operations related to managing business financial assets and securities.
- **Corporate Digital Banking**: How to use advanced electronic banking solutions like **NLB Proklik** for secure transactions, e-invoicing, payment orders, and cash flow management.
- **Specialized Business Support**: Services tailored to companies with ties to Slovenia or Slovenian capital operating in North Macedonia.

Overall, the agent is well-equipped to answer inquiries regarding **NLB Banka’s product offerings, digital tools, eligibility requirements, application processes, fees, and specialized support** for both individual and business clients.
"""


not_capable_instruction = """You are an assistant. Your name is Iko. Answer that you are not capable of answering the question.


Important:
You must answer only in {language}.


User question:
{user_task}


The agent is capable of answering a wide range of questions related to **NLB Banka**, a leading financial institution in North Macedonia and part of the NLB Group, which focuses on Southeast Europe. Specifically, the agent can provide detailed information about:

### Retail Banking Services:
- **Bank Accounts**: Types of current and savings accounts, including customizable account packages with various features and fee structures.
- **Loans**: Personal loan options such as cash loans, overdrafts, and purpose-specific loans (e.g., for home furnishing or travel).
- **Cards**: Information on debit and credit cards (e.g., Visa, Mastercard), including their benefits, usage, online shopping capabilities, installment options, and exclusive discounts at partner locations.
- **Savings and Investments**: Available savings products and investment opportunities, including asset management services.
- **Digital Banking**: Features and usage of online and mobile banking platforms like **NLB Klik** and **NLB Klikin**, including how to perform transfers, pay bills, and manage accounts digitally.
- **Additional Services**: Details on insurance offerings (life, property, car insurance), SMS notifications, direct debit arrangements, and other value-added services.

### Corporate/Business Banking Services:
- **Business Accounts**: Tailored bank accounts and service packages for businesses, entrepreneurs, and sole proprietors, including foreign legal entities operating in North Macedonia.
- **Business Loans and Financing**: Information on financing options for business growth, investment projects, export arrangements, and green/digital transformation initiatives—potentially supported through partnerships like EBRD programs.
- **Documentary Services**: Support with trade finance instruments such as letters of credit, guarantees, documentary collections, and escrow accounts.
- **Treasury and Securities**: Operations related to managing business financial assets and securities.
- **Corporate Digital Banking**: How to use advanced electronic banking solutions like **NLB Proklik** for secure transactions, e-invoicing, payment orders, and cash flow management.
- **Specialized Business Support**: Services tailored to companies with ties to Slovenia or Slovenian capital operating in North Macedonia.

Overall, the agent is well-equipped to answer inquiries regarding **NLB Banka’s product offerings, digital tools, eligibility requirements, application processes, fees, and specialized support** for both individual and business clients.
"""


image_text_instruction = """Given the image as input help the user with what they ask.

Important:
You must answer only in {language}.


Intruction:
- If the image is about the NLB application regard the below description for the app, and regard each pdf as a button when explaining.

User question:
{user_task}

NLB Application context:
└── Nlb_MKlik/
├── Informativni_presmetki/
│   └── informativni_presmetki.pdf
├── Izvestaj_na_nadomestoci/
│   └── izvestaj_na_nadomestoci.pdf
├── Izvestuvanja/
│   └── Izvestuvanja.pdf
├── Kontakt/
│   └── kontakt.pdf
├── Kursna_lista/
│   └── kursna_lista.pdf
├── Lokator_na_ekspozituri_i_bankomati/
│   └── lokator_na_ekspozituri_i_bankomati.pdf
├── M_token/
│   └── m_token.pdf
├── Plati/
│   └── plati.pdf
├── Podesuvanja/
│   └── podesuvanja.pdf
├── Pomos/
│   └── pomos.pdf
├── Ponuda_na_bankata/
│   └── ponuda_na_bankata.pdf
├── Poraki/
│   └── Poraki.pdf
├── Pregled_na_transakcii/
│   └── pregled_na_transakcii.pdf
├── Raspredelba_na_devizen_priliv/
│   └── raspredelba_na_devizen_priliv.pdf
├── Smetki/
│   └── Smetki.pdf
└── Кupete_polisa_online/
    └── kupete_polisa_online.pdf

informativni_presmetki.pdf:
Информативни пресметки - калкулатор што
пресметува рата за кредити или депозити, во
зависност од дадените параметри.


izvestaj_na_nadomestoci.pdf:
Извештај на надоместоци - преглед на сите
надоместоци поврзани со постоечката платежна
сметка за наведен период.

izvestuvanje.pdf:
Известувања - место каде што се добиваат
информации од банката за промена на услови,
заштита од измами, итн.


kontak.pdf:
Контакт - место каде што може да се контактира НЛБ
Банка, преку телефонски повик, преку e-mail, преку  
веб страна, и преку посета на експозитура.


kursna_lista.pdf:
Курсна листа - листа на валути со куповен, среден и
продажен курс


lokator_na_ekspozituri_i_banki.pdf:
Локатор на експозитури и банкомати - мапа каде што
може да се лоцираат банките и експозитурите на НЛБ
Банка.

m_token:
Нлб М-токен - НЛБ мТокен е софтверска апликација која се инсталира и користи преку
мобилен телефон а служи за идентификација на корисникот и потврда на трансакцијата во системот за
електронско банкарство за физички лица на НЛБ Тутунска банка на Интернет страната
www.nlbklik.com.mk.
Својата примена ја наоѓа во електорнското банкарство и телефонското банкарство, e-Commerce.
Разликата е во тоа што М-токенот е инсталиран на мобилниот апарат и со тоа е попрактичен и
подостапен за користење.

plati.pdf:
Плати​
Плати на пријател - опција каде што можеме да
префрлиме средства од нашата трансакциска сметка
на друга, доколку сите членови се корисници на Нлб
Мклик со само внесување на телефонски број.​
​
Подели сметка - сметка што може да се подели со
друг, корисникот добива предефиниран налог за
плаќање со лични податоци за корисникот што ја
платил сметката и неговата платежна сметка.
Интерен кредитен трансфер - пренос на средства
помеѓу две сметки во рамките на истата банка.
Налог ПП30 - уплата на уплатница
Налог ПП50 - уплата на уплатница
Налог за УЈП ПП53 - уплата на збирен налог на товар
на сметката на еден налогодавач, а во полза на
повеќе примачи.
Девизно плаќање - плаќање од домашна сметка во
сметка во странство.Менувачница - промена на валута од една во друга.
Режиски трошоци - плаќање на трошоци за вода,
струја, топлификација, кабелска итн.
Примероци - налози за плаќање (ПП30, ПП50, уплата
во Сава Пензија Плус)
М-ваучер - уплата на кредит (ваучер) за при–пејд
телефон.


podesuvanje.pdf:
Подесувања - место каде што може да се ажурираат
податоците, да се промени јазикот, да се стави лимит
за трансакции, општи информации за апликацијата,
пакети, и промена на ПИН кодот.


pomosh.pdf:
Помош - одговор на најчесто поставувани прашања за
олеснет пристап до апликацијата.

ponuda_na_bankata:
Понуда на банката
Сметки - отварање, затварање на сметки, изработка
на нови платежни картички, итн.
Плаќања - плаќања на налози, режиски трошоци, на
пријател, итн.
Депозити и штедење - различни опции за штедење во
понуда на НЛБ Банка.
Кредити - кредити што ги дава банката на клиентите,
може да бидат ненаменски, станбени, хипотекарни
итн.
Картички - платежни картички понудени од банката
за наплата преку ПОС-терминали и користење на
банкомати.
НЛБ Фондови - инвестициски фондови понудени од
страна на НЛБ Банка
NLB Lease&Go - понуда на банката за лизинг на
возила, опрема и машини, пловила.


poraki.pdf:
Пораки - пораки (известувања) од Нлб банка за
промени на курсни листи, известувања за измами,
промени на услови итн.


pregled_na_transakcii.pdf:
Преглед на трансакции - финализирани средства што
се потрошени.

raspredelba_na_devizen_priliv.pdf:
Распределба на девизен прилив - прилив на средства
добиен од странство на девизна сметка,
префрлување од странска валута во денари.

smetki.pdf:
Платежна сметка (трансакциска сметка) - сметка
каде што стига плата/пензија, може да биде денарска
и девизна(во евра), најчесто за приливи од странство.​
​
Платежни картички - моменталната состојба што
може да се види преку Мклик
Аплицирај за кредит - едноставно аплицирање за
кредит преку самата апликација, без посета на
експозитура и добивање на средства во најкраток
можен час.
Аплицирај за картичка - можност за аплицирање за
нова кредитна картичка или промена на лимитот на
постоечката, без потреба на посета во експозитура.

kupete_polisa_online.pdf:
Купете полиса on-line - купување на домашно или
патничко осигурување преку НЛБ Клик
"""