# Auto-French-EPUB
A tool to automatically translate an English EPUB into French

## Performances
Tested on the following hardware

    CPU: 12th Gen Intel(R) Core(TM) i9-12900HK 2.50 GHz
    GPU: NVIDIA GeForce RTX 3080 Ti Laptop GPU
    RAM: 64Go

Test case:

527 pages 
  GPU: ~40m

## Workflow:

    Extract the EPUB content
    Translate all the text content with Opus-mt-en-fr from the HuggingFace Hub
    Update the EPUB content, and write the translated EPUB.

## Requirements
### Hardware

A modern GPU or 32Go of RAM for CPU (will be much much slower, at least 5x)

### Software environment

Tested on Ubuntu 22.04

Python env

    torch with CUDA support (for GPU inference)
        Follow the install documentation from pytorch.org
    transformers library from HuggingFace
        pip install transformers
    BeautifulSoup
        pip install bs4
    yaml
        pip install yaml
    zipfile
        pip install zipfile
    tqdm
        pip install tqdm
    

### Usage

    Modify the config.yaml file to define the target folder containing your EPUB files, output folder...etc
    Run 'translate_EPUB_to_French.py', it will create an EPUB file with the same name as the input EPUB file.

## TODO

    make a gradio GUI

Context
This project is a testing ground to work with the HuggingFace plateform.
