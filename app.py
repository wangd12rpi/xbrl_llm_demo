import glob
import json
import os
import re

import gradio as gr
import dotenv
import pandas as pd
from fireworks.client import Fireworks

models = {"Llama 3.1 8B (Finetuned for tagging)": "accounts/d0nnw0n9-c1910b/models/finer",
          "Llama 3.1 8B (Finetuned for extraction)": "accounts/d0nnw0n9-c1910b/models/extraction",
          "Llama 3.1 8B (Base)": "accounts/fireworks/models/llama-v3p1-8b-instruct"}

from extract import inference, process_extract, process_tagging, process_generic


def read_jsonl(file):
    with open(file) as f:
        data = [json.loads(line) for line in f]
        return data


if __name__ == '__main__':
    with open('finer_example.json') as f:
        tagging_example = json.load(f)
    with open('extraction_example.json') as f:
        extraction_data = json.load(f)

    generic_jsonl_files = sorted(glob.glob("example_data/*.jsonl"))
    generic_data = [[x, read_jsonl(x)] for x in generic_jsonl_files]

    extraction_example = []
    for f in extraction_data:
        for x in extraction_data[f]:
            extraction_example.append([x, f])

    with gr.Blocks() as tagging:
        gr.Markdown("""
XBRL tagging is a key step in creating XBRL reports. Numerical entities in texts such as earning calls can to be tagged with US GAAP tags.

### Usage
* **Input:** Provide a sentence containing financial information.
* **Output:** Key entities and their corresponding US GAAP (Generally Accepted Accounting Principles) tags will be generated by the base model and our fine-tuned model.

""")
        gr.Interface(
            cache_examples=False,
            examples_per_page=20,
            fn=process_tagging,
            inputs=[
                gr.Textbox(label="Sentence")
            ],
            outputs=[gr.Dataframe(label="Llama 3.1 8b (base) output", headers=["Entites", "US GAAP tags"]),
                     gr.Dataframe(label="Llama 3.1 8b (fine-tuned for XBRL tagging) output",
                                  headers=["Entites", "US GAAP tags"]),
                     gr.Dataframe(label="Ground Truth Answer", headers=["Entites", "US GAAP tags"])],
            examples=[[x] for x in tagging_example.keys()],
            flagging_mode="never"
        )

    generic_blocks = {}
    for x in generic_data:
        name = x[0].replace("_", "").replace("example.jsonl",
                                                     "").replace(
            "exampledata/", "")
        with gr.Blocks() as blk:
            gr.Interface(
                fn=process_generic,
                cache_examples=False,
                inputs=[
                    gr.Textbox(label="Question"), gr.Textbox(visible=False, label="Ground Truth"),
                    gr.Textbox(label="Model", visible=False)
                ],
                outputs=[
                    gr.Text(label="Llama 3.1 8b (Base) output"),
                    gr.Text(label="Llama 3.1 8b (fine-tuned) output"),
                    gr.Text(label="Ground truth answer")
                ],
                examples=[[list(xi.keys())[0], [list(xi.values())][0][0],
                           name] for xi in x[1]],
                examples_per_page=20,
                flagging_mode="never"

            )
        generic_blocks[name] = (blk)

    with gr.Blocks() as extraction:
        gr.Markdown(
            """
            
Analyze an existing XBRL report with ease using our fine-tuned model as a chatbot. The model allows extraction of US GAAP tags, values, or financial formulas from the XBRL report.  

### Usage
* **Input:** A financial question and an XBRL file name.
* **Output:** The answer to the question will be generated by the base model and our fine-tuned model. Click on any numbers to locate the value in the XBRL report. 

            """
        )
        gr.Interface(
            fn=process_extract,
            cache_examples=False,
            inputs=[
                gr.Textbox(label="Question"),
                gr.Textbox(label="XBRL File Name"),
            ],
            outputs=[
                gr.HTML(label="Llama 3.1 8b (Base) output"),
                gr.HTML(label="Llama 3.1 8b (fine-tuned for XBRL analysis) output"),
                gr.HTML(label="Ground truth answer")
            ],
            examples=extraction_example,
            examples_per_page=20,
            flagging_mode="never"

        )

    with gr.Blocks(
            theme=gr.themes.Base()) as demo:
        gr.Markdown("# FinLoRA Demo\n\n### Benchmarking LoRA Methods for Fine-Tuning LLMs on Financial Datasets"
                    )
        gr.HTML("""<div>
  <a class="linkto" href="https://huggingface.co/collections/wangd12/finlora-adaptors-8bit-quantization-rank-8-684a45430e4d4a8d7ba205a4"><img src="https://raw.githubusercontent.com/wangd12rpi/FinLoRA/main/_images/models_btn.svg"></a>
  <a  class="linkto" href="https://finlora-docs.readthedocs.io/en/latest/"><img src="https://raw.githubusercontent.com/wangd12rpi/FinLoRA/main/_images/doc_btn.svg"></a>
  <a  class="linkto" href="https://arxiv.org/abs/2505.19819"><img src="https://raw.githubusercontent.com/wangd12rpi/FinLoRA/main/_images/paper_btn.svg"></a></div>

         <style>
        .linkto {
            display: inline-block;
            margin-right: 6px;
        }
        .html-container {
            padding: 0 !important;
        }
        body {
            font-family: system-ui, sans-serif !important;
        }
        </style>
        
""")

        gr.TabbedInterface([tagging, extraction] + [generic_blocks['buffett'], generic_blocks['ner'], generic_blocks['xbrlterm']],
                           ["XBRL Tagging", "XBRL Analysis", "Buffett Agent", "NER",
                            "XBRL Term"])

    demo.launch(share=True)
