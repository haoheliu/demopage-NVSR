from email.mime import audio
import os
import matplotlib
import matplotlib.pyplot as plt 
import librosa 
from librosa.display import specshow
import numpy as np 
import os
import re 
import random

plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = "16"
cmap = plt.get_cmap('inferno')
ROOT = "/Users/liuhaohe/projects/demopage-NVSR/resources"
PATTERN = "[ps][0-9]+_[0-9]+"
NUM=9
FILE_ID = []

def list_dir(path):
    ret = []
    for p in sorted(os.listdir(path)):
        if(os.path.isdir(os.path.join(path, p))):
            ret.append(p)
    return ret

def draw_spec(filepath):
    x,_ = librosa.load(filepath, sr=44100)
    stft_x = librosa.amplitude_to_db(np.abs(librosa.stft(x)))
    specshow(stft_x, sr=44100, x_axis='time', y_axis='linear', cmap=cmap)
    plt.xticks([])
    plt.xlabel("")
    plt.ylabel("")
    save_path = os.path.join(os.path.dirname(filepath), os.path.splitext(os.path.basename(filepath))[0]+".png")
    plt.savefig(save_path)
    plt.close()
    plt.clf()
    return save_path

def get_the_file_path_for_a_row(row_path, ancher):
    global FILE_ID
    ret = []
    valid_paths = list_dir(row_path)
    if(len(valid_paths) == 0): raise ValueError("Error: files not found in path %s" % row_path)
    files = [] 
    for file in os.listdir(os.path.join(row_path, valid_paths[0])):
        if(".wav" not in file[-5:]): continue
        else: files.append(file)
    files = sorted(files)
    if(len(FILE_ID) <= 1): FILE_ID = list(range(len(files)))
    if(ancher is None):
        index = random.randint(0, len(FILE_ID)) # todo, you may need to change this line from time to time
        # print(FILE_ID, ancher)
        ancher = files[FILE_ID[index]]
        FILE_ID.remove(FILE_ID[index])
    try:
        ancher = re.findall(PATTERN, os.path.basename(ancher))[0]
    except Exception as e:
        print(e, ancher)
    for col in valid_paths:
        for file in os.listdir(os.path.join(row_path, col)):
            if(ancher in file and (".wav" in file[-5:] or ".flac" in file[-5:])): 
                ret.append(os.path.join(row_path, col, file))
    return sorted(ret), valid_paths, ancher

def generate_div(html):
    return "<div> %s </div>" % html

def generate_table(html):
    return "<table> %s </table>" % html

def generate_row(html):
    return "<tr> %s </tr>" % html

def generate_col(html):
    return "<td> %s </td>" % html

def generate_audio(audio_path):
    return "<audio controls=\"\">"+"<source src=\"%s\" type=\"audio/wav\"></source></audio>" % audio_path;

def generate_img(img_path):
    return "<img src=\"%s\" alt=fname height=\"125\" width=\"200\" />" % img_path;

def generate_h2(content):
    return "<h2 id=\"%s%d\"> %s </h2>" % (content, random.randint(0, 99999), content)

def generate_h3(content):
    return "<h3 id=\"%s%d\"> %s </h3>" % (content, random.randint(0, 99999), content)

def generate_html(html):
    s = """
        <!DOCTYPE html>
        <html>
            <head>
                <style>
                    body {
                font-family: Arial, Helvetica, sans-serif;
                font-size: 15px;
                }
                
                    p{
                        margin-left: 60px;
                    }
                    h1{
                        margin-left: 30px;
                    }
                    h2{
                        margin-left: 40px;
                    }
                    h3{
                        margin-left: 50px;
                    }
                    h4{
                        margin-left: 60px;
                    }
                    table{
                        border: 1px solid black;
                        margin-left: 60px;
                        margin-right: auto;
                        text-align: center;
                    }
                    .center {
                        margin-left: auto;
                        margin-right: auto;
                    }
                </style>
            </head>
        <body>


        <div style="background-color:black;color:white;padding:30px;font-size: 60px;">Demo Of NVSR</div>
        <div style="background-color:lightgrey;padding:30px 30px 25px">
        </div>
        <div> %s </div>
        </body>
        </html>
    """ % html
    return s

def generate_table_htmls(file_paths, row_name, col_name):
    html = ""
    html += generate_col("")
    for name in col_name:
        html += generate_col(name[2:]) # ignore: a_
    html = generate_row(html)
    for group, name in zip(file_paths, row_name):
        html_audio = ""
        html_img = ""
        html_audio += generate_col(name[2:])
        html_img += generate_col("Spectrogram")
        for file in group:
            spec_path = draw_spec(file)
            html_audio += generate_col(generate_audio(file))
            html_img += generate_col(generate_img(spec_path))
        html_audio = generate_row(html_audio)
        html_img = generate_row(html_img)
        html += (html_audio + html_img)
    return generate_table(html)

def list_to_html(lst):
    result = ["<ul>"]
    for item in lst:
        if isinstance(item, list):
            result.append(list_to_html(item))
        else:
            result.append('<li><a href="#%s">%s</a></li>' % item)
    result.append("</ul>")
    return "".join(result)
    
def build_demo_html(path):
    from tqdm import tqdm
    html = ""
    # We generate NUM tables for each section
    for i in tqdm(range(NUM)):
        rows_info = []
        rows_name = []
        ancher = None
        # Get a table of data
        for row in list_dir(path):
            if(ancher is None):
                row_info, valid_paths, ancher = get_the_file_path_for_a_row(os.path.join(path, row), None) # todo Get a row of data
            else:
                row_info, valid_paths, ancher = get_the_file_path_for_a_row(os.path.join(path, row), ancher) # todo Get a row of data
            rows_info.append(row_info)
            rows_name.append(row)
        html += generate_h3(ancher+".wav") # Table title
        html += generate_table_htmls(rows_info, rows_name, valid_paths) # Generate a table
    return html
        
if __name__ == "__main__":
    # Dataset should be stored exactly the same with the example (labeled with a_, b_, ...)
    from bs4 import BeautifulSoup as bs
    final_html = "" # store the final result
    for testset in list_dir(ROOT):
        text_file = open(os.path.join("html",testset+".html"), "w") # store the result for each testset
        html = build_demo_html(os.path.join(ROOT, testset)) # Build a section
        html = generate_h2(testset[2:]) + html # Add the name of the section with the folder name
        soup = bs(html) # Prettify
        html = soup.prettify()  
        final_html += html
        text_file.write(html)
        text_file.close()
    text_file = open(os.path.join("html","output.html"), "w")
    
    # Add TOC
    soup = bs(final_html)
    toc = []
    current_list = toc
    previous_tag = None

    for header in soup.findAll(['h2', 'h3']):
        # import ipdb; ipdb.set_trace()
        header['id'] = header.get("id")
        header_id = header.get("id")
        if previous_tag == 'h2' and header.name == 'h3':
            current_list = []
        elif previous_tag == 'h3' and header.name == 'h2':
            toc.append(current_list)
            current_list = toc
        current_list.append((header_id, header.string))
        previous_tag = header.name

    if current_list != toc:
        toc.append(current_list)
    
    toc = list_to_html(toc)
    final_html = toc + final_html
    final_html = generate_html(final_html)
    text_file.write(final_html)
    text_file.close()     
    