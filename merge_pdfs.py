import os
from PyPDF2 import PdfMerger

source_dir = "./dir/"
merger = PdfMerger()

for item in os.listdir(source_dir):
    if item.endswith("pdf"):
        # print(item)
        merger.append(source_dir + item)

os.makedirs(source_dir + "output", exist_ok=True)
merger.write(source_dir + "output/merged.pdf")
merger.close()
