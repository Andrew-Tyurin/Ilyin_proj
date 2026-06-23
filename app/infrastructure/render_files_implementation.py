from datetime import date
from io import BytesIO

from reportlab.lib.colors import black, lightblue, lightgreen, lightcoral, white, gray, Color
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

from app.contracts.render_files_interface import InterfaceFilesPDF
from app.custom_enum import CurrencyEnum, OperationTypeEnum
from app.domain.dto import OperationHistoryDTO

pdfmetrics.registerFont(
    TTFont(
        'DejaVu',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    )
)


class ReportLabOperationFilesPDF(InterfaceFilesPDF):
    operation_name_ru: dict[str, str] = {
        OperationTypeEnum.INCOME: 'Доход',
        OperationTypeEnum.EXPENSE: 'Расход',
        OperationTypeEnum.TRANSFER_INCOME: 'Перевод, доход',
        OperationTypeEnum.TRANSFER_EXPENSE: 'Перевод, расход'
    }
    currency_symbols: dict[str, str] = {CurrencyEnum.RUB: '₽', CurrencyEnum.USD: '$', CurrencyEnum.EUR: '€'}
    bg_color_currency: dict[str, Color] = {'income': lightgreen, 'expense': lightcoral}

    def create(
            self,
            operations: list[OperationHistoryDTO],
            user_name: str,
            date_from: date,
            date_to: date,
            timezone: str
    ) -> BytesIO:

        content = [
            ('№', '№ операции', 'Дата операции', '№ кошелька', 'Имя кошелька', 'Тип операции', 'Сумма'),
        ]
        list_style = [
            ('FONT', (0, 0), (-1, 0), 'DejaVu', 9, 9),
            ('FONT', (0, 1), (-1, -1), 'DejaVu', 8, 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, black),
            ('BOX', (0, 0), (-1, -1), 0.25, black),
            ('BACKGROUND', (0, 0), (-1, 0), gray),
            ('TEXTCOLOR', (0, 0), (-1, 0), white)
        ]

        for index, operation in enumerate(operations, 1):
            list_style.append(
                ('BACKGROUND', (6, index), (6, index), self.bg_color_currency.get(operation.operation.type, lightblue))
            )
            content.append(
                (
                    index,  # №
                    operation.operation.id,  # № операции
                    operation.operation.created_at.strftime('%d.%m.%Y %H:%M:%S %z'),  # Дата операции
                    operation.wallet_id,  # № кошелька
                    operation.wallet_name,  # Имя кошелька
                    self.operation_name_ru.get(operation.operation.type),  # Тип операции
                    f"{operation.operation.amount} {self.currency_symbols.get(operation.currency)}",  # Сумма
                )
            )

        if not operations:
            content.append((1, "Нет", "Операций", "в", "этот", "период", "времени"))

        table_styles = TableStyle(list_style)
        styles = getSampleStyleSheet()

        title_style = styles['Title']
        title_style.fontName = "DejaVu"

        body_style = styles['Normal']
        body_style.fontName = "DejaVu"
        body_style.fontSize = 10
        body_style.leading = 12
        body_style.alignment = 1
        body_style.spaceAfter = 12

        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer)
        content_table = Table(content, style=table_styles)

        title_text = "Finance Tracker"
        body_text = f"""
        История операций пользователя: {user_name}<br/>
        В промежутке: {date_from.strftime('%d.%m.%Y')} - {date_to.strftime('%d.%m.%Y')}<br/>
        Часовой пояс: {timezone}
        """

        pdf.build(
            [
                Paragraph(title_text, title_style),
                Paragraph(body_text, body_style),
                content_table
            ]
        )
        buffer.seek(0)
        return buffer
