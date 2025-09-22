import os
import subprocess
import csv
import codecs
from datetime import datetime

class InvoiceGenerator:
    def __init__(self, base_output_dir="invoices"):
        """Initialize with base output directory"""
        self.base_output_dir = base_output_dir
        if not os.path.exists(base_output_dir):
            os.makedirs(base_output_dir)

    def _get_term_dir(self, term_data):
        """Get term-specific output directory"""
        term_dir = os.path.join(self.base_output_dir, f"term_{term_data['term']}")
        if not os.path.exists(term_dir):
            os.makedirs(term_dir)
        return term_dir

    def generate_from_csv(self, csv_path):
        """Generate invoices from CSV file"""
        try:
            data = self._process_csv(csv_path)
            return [self.generate_invoice(row) for row in data]
        except Exception as e:
            print(f"Error generating invoices: {e}")
            return []

    def _process_csv(self, csv_path):
        """Process CSV file and return structured data"""
        processed_data = []
        with open(csv_path) as data:
            reader = csv.reader(data, delimiter=',')
            next(reader)  # Skip header
            next(reader)  # Skip second row as it is formatting only
            for row in reader:
                if row:  # Skip empty rows
                    processed_data.append({
                        'name': row[0].strip(),
                        'invoice_number': row[1],
                        'invoice_date': row[2],
                        'tuition_level': row[3],
                        'tuition_class': row[4],
                        'term': row[5],
                        'start_date': row[6],
                        'end_date': row[7],
                        'no_of_lessons': row[8],
                        'lesson_rate': row[9],
                        'lesson_total': row[10],
                        'discount_rate': row[11],
                        'discount_total': row[12],
                        'refund_reason': row[13],
                        'refund_rate': row[14],
                        'refund_quantity': row[15],
                        'refund_total': row[16],
                        'trial_lesson_date': row[17],
                        'trial_fee': row[18],
                        'grand_total': row[19],
                        'year': row[20],
                        'student_id': row[21]
                    })
        return processed_data

    def generate_invoice(self, data):
        """Generate single invoice"""
        try:
            tex_path = self._create_tex_file(data)
            return self._generate_pdf(tex_path)
        except Exception as e:
            print(f"Error generating invoice for {data['name']}: {e}")
            return None

    def _generate_latex_content(self, data):
        """Generate LaTeX content"""
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
            \\ Tuition Subject: (%s) 
            \\
            \\ Term %s Lessons
            \\ For lessons from %s to %s & %s & \$%s & \$%s''' % (data['grand_total'], data['name'], data['invoice_number'], data['invoice_date'], data['tuition_class'], data['term'], data['start_date'], data['end_date'], data['no_of_lessons'], data['lesson_rate'], data['lesson_total'])

        if len(data['discount_rate']) > 0 and float(data['discount_rate']) > 0:
            insert = r'''
        \\
        \\ Discounts
        \\ For lessons from %s to %s & %s & - \$%s & - \$%s''' % (data['start_date'], data['end_date'], data['no_of_lessons'], data['discount_rate'], data['discount_total'])
            content += insert

        if len(data['refund_reason']) > 0:
            insert = r'''
        \\
        \\ Payment Refund
        \\ Excess payments for lesson(s) on %s & %s & - \$%s & - \$%s''' % (data['refund_reason'], data['refund_quantity'], data['refund_rate'], data['refund_total'])
            content += insert

        if len(data['trial_lesson_date']) > 0:
            insert = r'''
        \\
        \\ Trial Lesson
        \\ Trial lesson on %s & %s & \$%s & \$%s''' % (data['trial_lesson_date'], data['no_of_lessons'], data['trial_fee'], data['grand_total'])
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
        \pagebreak''' % (data['grand_total'])

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
        \\ & {\scriptsize 121 碧山 12 街 , #01-89, 新加坡 570121 | 电话号码: 6980 3149 }
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
            \\ 补习科目: (%s) & & & 
            \\
            \\ 第 %s 学期课程
            \\ 从 %s 至 %s & %s & \$%s & \$%s'''%  (data['grand_total'], data['name'], data['invoice_number'], data['invoice_date'], data['tuition_class'], data['term'], data['start_date'], data['end_date'], data['no_of_lessons'], data['lesson_rate'], data['lesson_total'])


        content += insert

        if len(data['discount_rate']) > 0 and float(data['discount_rate']) > 0:
            insert = r'''

        \\ 
        \\ 折扣
        \\ 从 %s 至 %s & %s & - \$%s & - \$%s''' % (data['start_date'], data['end_date'], data['no_of_lessons'], data['discount_rate'], data['discount_total'])
            content += insert

        if len(data['refund_reason']) > 0:
            insert = r'''

        \\
        \\ 学费退款
        \\ 额外支付 %s 的课程学费 & %s &- \$%s & - \$%s''' % (data['refund_reason'], data['refund_quantity'], data['refund_rate'], data['refund_total'])
            content += insert
        
        if len(data['trial_lesson_date']) > 0:
            insert = r'''
        \\
        \\ 试课学费
        \\ 试课日期：%s & %s & \$%s & \$%s''' % (data['trial_lesson_date'], 1, data['trial_fee'], data['trial_fee'])
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
        \end{document}''' % (data['grand_total'])

        content += insert

        return content
    
    def _create_tex_file(self, data):
        """Create LaTeX file in term-specific directory"""
        term_dir = self._get_term_dir(data)
        filename = f"{data['student_id']}_{data['name']}_{data['year']}_Term_{data['term']}_Invoice.tex"
        if len(data['invoice_number']) > 9:
            filename = f"{data['student_id']}_{data['name']}_{data['year']}_Term_{data['term']}_Invoice_({data['invoice_number']}).tex"
        
        filepath = os.path.join(term_dir, filename)
        content = self._generate_latex_content(data)
        
        with codecs.open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def _generate_pdf(self, tex_path):
        """Generate PDF in term-specific directory"""
        try:
            output_dir = os.path.dirname(tex_path)
            
            #remove existing invoice for that student in that term.

            cmd = ['xelatex', '-interaction', 'nonstopmode', 
                   '-output-directory', output_dir, tex_path]
            subprocess.run(cmd)
            
            pdf_path = tex_path.replace('.tex', '.pdf')
            self._cleanup_temp_files(tex_path)
            
            return pdf_path if os.path.exists(pdf_path) else None
            
        except subprocess.CalledProcessError as e:
            print(f"PDF generation failed: {e}")
            return None
    
    def _cleanup_temp_files(self, tex_path):
        """Cleanup temporary files"""
        temp_files = [tex_path.replace('.tex', ext) for ext in ['.aux', '.log', '.out', '.tex']]
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)

if __name__ == "__main__":
    generator = InvoiceGenerator()
    generator.generate_from_csv('private/data.csv')