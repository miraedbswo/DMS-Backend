from openpyxl import Workbook

from flask import make_response, send_from_directory

from app.views.v2 import BaseResource

from utils.excel_style_manager import ready_applyment_worksheet


class ExcelDownload(BaseResource):
    def __init__(self, model, filename, extension='xlsx'):
        self.model = model
        self.filename = filename
        self.extension = extension
        self.filename_full = '{}.{}'.format(self.filename, self.extension)

        super(ExcelDownload, self).__init__()

    def ready_worksheet(self):
        wb = Workbook()
        ws = wb.active

        ready_applyment_worksheet(ws)

        return wb, ws

    def save_excel(self, wb):
        wb.save('{}'.format(self.filename_full))
        wb.close()

    def get_response_object_with_excel_file(self):
        resp = make_response(send_from_directory('../', self.filename_full))
        resp.headers.extend({'Cache-Control': 'no-cache'})

        return resp

    def get_status(self, apply):
        raise NotImplementedError()
