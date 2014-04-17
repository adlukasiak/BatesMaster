from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import StringIO

orig_pdf = PdfFileReader(open("document.pdf", "rb"))
#print "document1.pdf has %d pages." % input1.getNumPages()
num_pages = orig_pdf.getNumPages()
page_size = orig_pdf.getPage(0).mediaBox

### inputs ####
#font_size = 10
#prefix = "BB"
#starting_number_str = "00067"
#mode = "right" #"left" and "center"

input_config = {
                "left"  : {"mode":"left"  ,"font_size":10,"starting_num":""     ,"prefix":"CONFIDENTIAL - ATTORNEYS EYES ONLY"},
                "right" : {"mode":"right" ,"font_size":10,"starting_num":"00067","prefix":""},
                }
#input_config = {
#                "left"  : {"mode":"left"  ,"font_size":10,"starting_num":""     ,"prefix":"CONFIDENTIAL - ATTORNEYS EYES ONLY"},
#                "center": {"mode":"center","font_size":10,"starting_num":""     ,"prefix":""},
#                "right" : {"mode":"right" ,"font_size":10,"starting_num":"00067","prefix":""},
#                }

### and figure few things out based on inputs ###
height = float(page_size[2]/72)*inch
width = float(page_size[3]/72)*inch
margin = 0.5*inch

config = {
          "right" :{"x":width-0.5*inch,"y":margin, "func": lambda x,y,text : canv.drawRightString(x,y,text)},
          "left"  :{"x":margin        ,"y":margin, "func": lambda x,y,text : canv.drawString(x,y,text)},
          "center":{"x":width/2       ,"y":margin, "func": lambda x,y,text : canv.drawCentredString(x,y,text)}
          }

# the temp file should be same size as the original document
packet = StringIO.StringIO()
canv = canvas.Canvas(packet,pagesize=(width,height))

for i in range(0,num_pages):
    for j in input_config:
        
        #figure out few things about the starting number
        num_length = len(str(input_config[j]["starting_num"]))
        page_number_offset = int(input_config[j]["starting_num"] if input_config[j]["starting_num"] != "" else -1)

        canv.setFont("Times-Roman", input_config[j]["font_size"]) #need to reset font for each page
            
        bates = str(canv.getPageNumber()+page_number_offset).zfill(num_length) if page_number_offset > 0 else ""
        
        text = input_config[j]["prefix"] + bates
        mode = input_config[j]["mode"]
        #print canv.getPageNumber(),text, width, config[mode]["x"]
    
        config[mode]["func"](config[mode]["x"],config[mode]["y"],text)
    canv.showPage() #move to the next page
canv.save()

# Time to merge
#move to the beginning of the StringIO buffer
packet.seek(0)
new_pdf = PdfFileReader(packet)
# read your existing PDF
output = PdfFileWriter()
# add the "watermark" (which is the new pdf) on the existing page
for i in range(0,num_pages):
    page = orig_pdf.getPage(i)
    page.mergePage(new_pdf.getPage(i))
    output.addPage(page)
# finally, write "output" to a real file
outputStream = file("document_bates.pdf", "wb")
output.write(outputStream)
outputStream.close()
