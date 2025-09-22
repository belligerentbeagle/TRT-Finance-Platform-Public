import argparse
import os
import subprocess
import csv
import codecs

all = []
a = []

with open('private/data.csv') as data:
    reader = csv.reader(data, delimiter=',')
    line = 0
    for row in reader:
        if line > 0:
            a = []
            for column in row:
                a.append(column)
        elif line == 0:
            line = 1
        all.append(a)
all = all[2:]

for i in range(len(all)):
    name = all[i][0]
    if name[-1] == ' ':
        name = name[:-1]
    invoice_number = all[i][1]
    invoice_date = all[i][2]
    tuition_level = all[i][3]
    tuition_class = all[i][4]
    term = all[i][5]
    start_date = all[i][6]
    end_date = all[i][7]
    no_of_lessons = all[i][8]
    lesson_rate = all[i][9]
    lesson_total = all[i][10]
    discount_rate = all[i][11]
    discount_total = all[i][12]
    refund_reason = all[i][13]
    refund_rate = all[i][14]
    refund_quantity = all[i][15]
    refund_total = all[i][16]
    trial_lesson_date = all[i][17]
    trial_fee = all[i][18]
    grand_total = all[i][19]
    year = all[i][20]

    filename = str(name)+' '+str(year)+' Term '+str(term)+' Invoice.tex'
    if len(invoice_number) > 9:
        filename = str(name)+' '+str(year)+' Term '+str(term)+' Invoice (' + str(invoice_number[-1]) + ').tex'
    
    filelog = str(name)+' '+str(year)+' Term '+str(term)+' Invoice.log'
    if len(invoice_number) > 9:
        filelog = str(name)+' '+str(year)+' Term '+str(term)+' Invoice (' + str(invoice_number[-1]) + ').log'

    content = r'''\documentclass[20pt, a4paper]{report}
    \usepackage{graphicx}
    \graphicspath{{images/}}
    \usepackage{tabularx}
    \usepackage{multirow}
    \usepackage{multicol}
    \usepackage[UTF8]{ctex}
    \usepackage{geometry}
    \geometry{
    a4paper,
    total={170mm,257mm},
    left=20mm,
    top=20mm,
    }
    \begin{document}
    \begin{tabularx}{\textwidth}{X c c c}
        \\ 
        \\ 
    \end{tabularx} 
    \begin{tabularx}{\textwidth}{X c c c}
        \hspace{-20pt} \multirow{2}{*}{\includegraphics[scale=0.12]{public/assets/TRT_Logo.png}} & \textbf{{\huge The Rationale Thinking Learning Centre}}
    \\ & {\large General Paper and IP English tuition specialist}\
    \\ &
    \\ & {\scriptsize Company Registration No.: 201222890K | www.therationalethinking.com}
    \\ & {\scriptsize 121 Bishan Street 12, #01-89, Singapore 570121 | Direct Dial: 6980 3149}
    \end{tabularx} 

    \begin{tabularx}{\textwidth}{X C C}
        \\ 
        \\ 
        \\
    \end{tabularx} 

    \begin{tabularx}{\textwidth}{X | C C}
        \\ \textbf{Invoice to the Parents/ Guardian of:} & \textbf{Total Amount Due:} & \textbf{\$%s}
        \\
        \\ %s & {Invoice Number:} & %s
        \\ & {Invoice Date:} & %s
    \end{tabularx} 

    \begin{tabularx}{\textwidth}{X C C C}
        \\
        \\ \textbf{Course Fee Description} & Quantity & Rate & Amount
        \\ Tuition Subject: %s (%s) 
        \\
        \\ Term %s Lessons
        \\ For lessons from %s to %s & %s & \$%s & \$%s''' % (grand_total, name, invoice_number, invoice_date, tuition_level, tuition_class, term, start_date, end_date, no_of_lessons, lesson_rate, lesson_total)

    if len(discount_rate) > 0 and float(discount_rate) > 0:
        insert = r'''
    \\
    \\ Discounts
    \\ For lessons from %s to %s & %s & - \$%s & - \$%s''' % (start_date, end_date, no_of_lessons, discount_rate, discount_total)
        content += insert
    
    if len(refund_reason) > 0:
        insert = r'''
    \\
    \\ Payment Refund
    \\ Excess payments for lesson(s) on %s & %s & - \$%s & - \$%s''' % (refund_reason, refund_quantity, refund_rate, refund_total)
        content += insert
    
    if len(trial_lesson_date) > 0:
        insert = r'''
    \\
    \\ Trial lesson
    \\ Trial lesson on %s & %s & \$%s & \$%s''' % (trial_lesson_date, 1, trial_fee, trial_fee)
        content += insert
    
    insert = r'''
    \end{tabularx} 
    \vspace{40pt}
    \begin{flushright}
    \textbf{\large GRAND TOTAL: \$%s}
    \end{flushright}
    
    \vspace{60pt}
    \hspace{0pt} \textbf{{See Next Page for Payment Methods}}
    \pagebreak
    \\ \textbf{{Payment Methods}}
    \\ {QR Payment | Bank Transfer | Cash | Cheque}
    \vspace{20pt}
    \\ \textbf{Company Payment Details}
    \\ {QR Payment supports both \textbf{\textit{PayNow}} and \textbf{\textit{Paylah!}}}, please enter the student's full name and the invoice number to the reference code section. 
    \\ {Company UEN No.: \textbf{\textit{201222890K}}}
    \\ \includegraphics[scale=0.3]{public/assets/TRT_QR.png}
    \\ For Internet Banking, please make payments to \textbf{\textit{OCBC 713008225001}}. Please ensure that when adding TRT as recipient, enter the student's name as ‘Your Initials’
    \\ For Cheque payments, please make cheque payable to \textbf{\textit{The Rationale Thinking Learning Centre Pte Ltd}}
    \vspace{20pt}
    \\ \textbf{Post Payment Procedure}
    \\ {If you are making payment electronically, \textbf{please reply the email or message} with which you received this invoice \textbf{with the Proof of Payment}, and \textbf{rename the email subject as: student's name, invoice number}. Do ensure that your transaction details (i.e. Amount paid, Transaction Reference Number, etc.) are visible. Please make the necessary payment(s) within 14 days from the date of your invoice.}
    \\ {For physical payments (Cash or Cheque), do make the payment over the counter at our Centre. Please make the necessary payment(s) within 14 days from the date of your invoice.}
    \\
    \\
    \\ \textbf{Should there be any problems with payments, please contact us at trtbilling@therationalethinking.com}
    \pagebreak''' % (grand_total)

    content += insert

    insert = r'''
    \begin{tabularx}{\textwidth}{X c c c}
        \\ 
        \\ 
    \end{tabularx} 
    \begin{tabularx}{\textwidth}{X c c c}
        \hspace{-20pt} \multirow{2}{*}{\includegraphics[scale=0.12]{public/assets/TRT_Logo.png}} & \textbf{{\huge The Rationale Thinking Learning Centre}}
    \\ & {\large General Paper and IP English tuition specialist}\
    \\ &
    \\ & {\scriptsize 公司注册号: 201222890K | www.therationalethinking.com/zh-hans}
    \\ & {\scriptsize 121 碧山 12 街 , #01-89, 新加坡 570121 | 电话号码: 6980 3149}
    \end{tabularx} 

    \begin{tabularx}{\textwidth}{X C C}
        \\ 
        \\ 
        \\
    \end{tabularx} 

    \begin{tabularx}{\textwidth}{X | C C}
        \\ \textbf{致以下学生的家长或监护人:} & \textbf{总学费:} & \textbf{\$%s}
        \\
        \\ %s & {发票号码:} & %s
        \\ & {开票日期:} & %s
    \end{tabularx} 

    \begin{tabularx}{\textwidth}{X C C C}
        \\
        \\ \textbf{学费详情} & 课程总数 & 单次数额 & 总数额
        \\ 补习科目: %s (%s) & & & 
        \\
        \\ 第 %s 学期课程
        \\ 从 %s 至 %s & %s & \$%s & \$%s'''% (grand_total, name, invoice_number, invoice_date, tuition_level, tuition_class, term, start_date, end_date, no_of_lessons, lesson_rate, lesson_total)

    content += insert

    if len(discount_rate) > 0 and float(discount_rate) > 0:
        insert = r'''
    \\
    \\ 折扣
    \\ 从 %s 至 %s & %s & - \$%s & - \$%s''' % (start_date, end_date, no_of_lessons, discount_rate, discount_total)
        content += insert
    
    if len(refund_reason) > 0:
        insert = r'''
    \\
    \\ 学费退款
    \\ 额外支付 %s 的课程学费 & %s &- \$%s & - \$%s''' % (refund_reason, refund_quantity, refund_rate, refund_total)
        content += insert
    
    if len(trial_lesson_date) > 0:
        insert = r'''
    \\
    \\ 试课学费
    \\ 试课日期：%s & %s & \$%s & \$%s''' % (trial_lesson_date, 1, trial_fee, trial_fee)
        content += insert
    
    insert = r'''
    \end{tabularx} 

    \vspace{40pt}
    \begin{flushright}
    \textbf{\large 总学费: \$%s}
    \end{flushright}
    
    \vspace{60pt}
    \hspace{0pt} \textbf{{支付方式请见下一页}}
    \pagebreak
    \\ \textbf{{支付方式}}
    \\ {扫码支付 | 银行转账 | 现金 | 支票}
    \vspace{20pt}
    \\ \textbf{付款详情}
    \\ {本公司支持 \textbf{\textit{Paynow}} 和 \textbf{\textit{Paylah!}} 软件扫码付款}。请在参考编号处输入学生姓名以及发票号码。
    \\ {本公司的 UEN 号码为: \textbf{\textit{201222890K}}}
    \\ \includegraphics[scale=0.3]{public/assets/TRT_QR.png}
    \\ 用银行转账时，请将学费转账给本公司账户： \textbf{\textit{OCBC 713008225001}}。请注意在添加收款人时将学生的全名输入到‘您的姓名首字母’处。
    \\ 用支票支付时，请开支票给： \textbf{\textit{The Rationale Thinking Learning Centre Pte Ltd}}
    \vspace{20pt}
    \\ \textbf{付款后注意事项}
    \\ {如果您使用电子支付，\textbf{请回复这封电邮或短信}，并\textbf{附上转账的截图}。\textbf{请将邮件的主题命名为：学生英文全名，发票号码}。发送付款凭证之前请确保您截图里的付款资料（例：支付数目、付款编号等）可见。请在开票日期 14 天内完成付款。}
    \\ {如果您要交现金或开支票，请到本中心的柜台把学费交给我们的职员。请在开票日期 14 天内完成付款。}
    \\
    \\
    \\ \textbf{如果您在付款时遇到任何问题，请发送邮件到 trtbilling@therationalethinking.com 联系我们。} 
    \end{document}''' % (grand_total)

    content += insert

    with codecs.open(filename, 'a', encoding='utf-8') as f:
        f.write(content)

    print(filename, 'has been generated')
    
    # cmd = ['pdflatex', '-interaction', 'nonstopmode', filename]
    # proc = subprocess.Popen(cmd)
    cmd = ['xelatex', '-interaction', 'nonstopmode', '-output-directory', '.', filename]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.communicate()
    
    os.unlink(filelog)
