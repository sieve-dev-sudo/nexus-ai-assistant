"""
ui/report_pdf.py
──────────────────
Turns the report HTML from LessonEngine.build_report_html() into an
A4 PDF file, using only what ships with PyQt5 (QTextDocument +
QPrinter), so there's no extra dependency and it still works offline
and inside the PyInstaller build.
"""

from PyQt5.QtCore import QMarginsF, QSizeF
from PyQt5.QtGui import QPageLayout, QPageSize, QTextDocument
from PyQt5.QtPrintSupport import QPrinter


def export_pdf(html: str, filepath: str) -> bool:
    """Render the given HTML to an A4 PDF at filepath. Returns True on success."""
    try:
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(filepath)
        printer.setPageLayout(QPageLayout(
            QPageSize(QPageSize.A4), QPageLayout.Portrait,
            QMarginsF(14, 14, 14, 14), QPageLayout.Millimeter,
        ))
        printer.setDocName("Nexus AI Learning Report")
        printer.setCreator("Nexus AI : Python Assistant")

        doc = QTextDocument()
        doc.setDocumentMargin(0)
        doc.setHtml(html)
        # Lay the document out at the printable page size, so tables use
        # the full page width and Qt paginates long quiz histories itself.
        doc.setPageSize(QSizeF(printer.pageRect(QPrinter.Point).size()))
        doc.print_(printer)
        return printer.printerState() != QPrinter.Error
    except Exception:  # never crash the app over an export
        return False
