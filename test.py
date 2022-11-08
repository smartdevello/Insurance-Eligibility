from PyPDF2 import PdfFileMerger
import os


def reset_eof_of_pdf_return_stream(pdf_stream_in:list):
    # find the line position of the EOF
    actual_line = 0
    for i, x in enumerate(txt[::-1]):
        if b'%%EOF' in x:
            actual_line = len(pdf_stream_in)-i
            print(f'EOF found at line position {-i} = actual {actual_line}, with value {x}')
            break

    # return the list up to that point
    return pdf_stream_in[:actual_line]


abs_path = os.path.abspath(os.path.dirname(__file__))
pdf_path= abs_path + "/" + "west_tmp55534.pdf"

# opens the file for reading
with open(pdf_path, 'rb') as p:
    txt = (p.readlines())

# get the new list terminating correctly
txtx = reset_eof_of_pdf_return_stream(txt)

# write to new pdf
with open(pdf_path, 'wb') as f:
    f.writelines(txtx)


merger = PdfFileMerger()
merger.append(pdf_path)

with open( 'west_cmn.pdf', "wb") as fout:
    merger.write(fout)

x = 0