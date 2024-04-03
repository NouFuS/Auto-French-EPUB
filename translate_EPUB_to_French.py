import zipfile
from bs4 import BeautifulSoup
from tqdm import tqdm
import torch
from transformers import pipeline
import yaml
from pprint import pprint
import os

def process_file(folder_path, filename, output_folder, use_gpu, debug):
    if use_gpu:
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
    else:
        device = 'cpu'

    print("Device:", device)
    # pipe_translate = pipeline("translation", model="Helsinki-NLP/opus-mt-en-fr", device=device) # Bad perfs
    pipe_translate = pipeline("translation", model="Helsinki-NLP/opus-mt-tc-big-en-fr", batch_size=16, device=device) # Decent perfs, quite fast
    # pipe_translate = pipeline("translation", model="jbochi/madlad400-3b-mt", batch_size=16, device=device) # Verfy slow, haven't found the right conf to make it work properly
    # test_text = "Hello, I'm Quentin, how are you today? I have a medical problem I'd like to discuss."
    # translation = pipe_translate(test_text)
    # print("Translation:", translation)

    debug_chapter = 15
    debug_i = -1

    # file_name = "epubs/King of Scars by Leigh Bardugo.epub"
    # filepath = "epubs/Rule of Wolves.epub"
    filepath = os.path.join(folder_path, filename)

    input_archive = zipfile.ZipFile(filepath, "r")
    if debug:
        output_archive = zipfile.ZipFile(os.path.join(output_folder,filename)+"_traduction_debug.epub", "w")
    else:
        output_archive = zipfile.ZipFile(os.path.join(output_folder,filename)+"_traduction.epub", "w")
    file_list = input_archive.infolist()
    print(file_list)

    for x in tqdm(range(0, len(file_list))):
        item = input_archive.open(file_list[x])
        content = item.read()
        
        if file_list[x].filename.endswith(".html"):# and "0009" in file_list[x].filename:
            debug_i +=1
            if debug and debug_i != debug_chapter:
                continue
        
            html = input_archive.read(file_list[x].filename)
            soup = BeautifulSoup(html, 'html.parser')
            for i in soup.find_all('p'):#, ["tx", "txt"]):
                sentences = i.text.split(". ")
                
                # Making sure there are no words only in uppercase (otherwise then don't get translated...)
                for idx, sentence in enumerate(sentences):
                    if "." not in sentence:
                        sentence = sentence + ". " # Adding the ending dot back. Otherwise some sentences don't make sense and get translated wrong
                        sentences[idx] = sentence
                    found_upper = False
                    for word in sentence.split(" "):
                        if word.isupper():
                            found_upper = True
                            sentence = sentence.replace(word, word.lower())
                            # print("Replaced Upper case words:", word, "by", word.lower())
                            # print("Updated sentence (ONGOING):", sentence)
                    if found_upper:
                        sentence = sentence[0].upper() + sentence[1:]
                        # print("Corrected sentence:", sentence)
                        sentences[idx] = sentence
                        # print("by:", sentences[idx])

                # print("\n\nFound to translate:", sentences)
                translated = pipe_translate(sentences)
                # print("Translated text:", translated)
                
                translated_aggregated = "<p class=\"txt\">" + translated[0]["translation_text"]
                
                for sentence in translated[1:]:
                    translated_aggregated += " " + sentence["translation_text"]
                translated_aggregated += "</p>\n"
                i.replace_with(translated_aggregated)

            output_archive.writestr(file_list[x].filename, soup.prettify("utf-8", formatter=None))
            # pprint(soup.prettify("utf-8"))
        else:
            #For the other file types, simply copy the original content:
            output_archive.writestr(file_list[x].filename, content)

    input_archive.close()
    output_archive.close()


def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


if __name__ == "__main__":    
    config_file = "config.yaml"
    # config_file = "config_debug.yaml"
    config = read_yaml(config_file)

    pprint(config)

    if config["FILES"]["process_single_file"]:
        process_file(
                        config["FILES"]["folder_path"], 
                        config["FILES"]["filename"], 
                        config["FILES"]["output_folder"],
                        use_gpu=config["INFERENCE"]["use_gpu"],
                        debug=config["INFERENCE"]["debug"])
    else:
        files = os.listdir(config["FILES"]["folder_path"])
        
        for file in tqdm(files):
            print("\n\nProcessing:", file)
            if True:
                ## Filter not working because of bad parsing of '.' in filenames
                # not config["FILES"]["skip_if_srt_exists"] or (config["FILES"]["skip_if_srt_exists"] and not os.path.exists(os.path.join(config["FILES"]["output_folder"], file.split(".")[0]+".fre.srt"))):
                process_file(
                            config["FILES"]["folder_path"], 
                            file, 
                            config["FILES"]["output_folder"],
                            use_gpu=config["INFERENCE"]["use_gpu"],
                            debug=config["INFERENCE"]["debug"])
            else:
                print("Translated EPUB exists, skip.")