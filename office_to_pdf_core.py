# =============================================================================
# AllTools — Office to PDF Conversions (COM Automation)
# Author  : Ali Qureshi
# License : MIT
# =============================================================================
import os
import comtypes.client

def word_to_pdf(input_path, output_path):
    """
    Converts a Word document to PDF using MS Word COM automation.
    """
    input_path = os.path.abspath(input_path)
    output_path = os.path.abspath(output_path)
    
    word = comtypes.client.CreateObject('Word.Application')
    word.Visible = False
    doc = word.Documents.Open(input_path)
    
    # 17 is the format code for wdFormatPDF
    doc.SaveAs(output_path, FileFormat=17)
    doc.Close()
    word.Quit()
    return output_path

def excel_to_pdf(input_path, output_path):
    """
    Converts an Excel spreadsheet to PDF using MS Excel COM automation.
    """
    input_path = os.path.abspath(input_path)
    output_path = os.path.abspath(output_path)
    
    excel = comtypes.client.CreateObject('Excel.Application')
    excel.Visible = False
    
    wb = excel.Workbooks.Open(input_path)
    
    # 0 is the format code for xlTypePDF
    wb.ExportAsFixedFormat(0, output_path)
    wb.Close(False)
    excel.Quit()
    return output_path

def ppt_to_pdf(input_path, output_path):
    """
    Converts a PowerPoint presentation to PDF using MS PowerPoint COM automation.
    """
    input_path = os.path.abspath(input_path)
    output_path = os.path.abspath(output_path)
    
    powerpoint = comtypes.client.CreateObject('Powerpoint.Application')
    
    # PowerPoint requires it to be visible or opened in a specific way sometimes, but we try invisible first
    # With-Window=False (0)
    deck = powerpoint.Presentations.Open(input_path, WithWindow=0)
    
    # 32 is the format code for ppSaveAsPDF
    deck.SaveAs(output_path, 32)
    deck.Close()
    powerpoint.Quit()
    return output_path
