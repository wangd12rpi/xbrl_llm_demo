import json
import os
import re
from xml.etree import ElementTree

import gradio as gr
import dotenv
import requests
from fireworks.client import Fireworks
from urllib.parse import quote

with open('extraction_example.json') as f:
    extraction_data = json.load(f)

models = {"Llama 3.1 8B (Finetuned for tagging)": "accounts/d0nnw0n9-c1910b/models/finer",
          "Llama 3.1 8B (Finetuned for extraction)": "accounts/d0nnw0n9-c1910b/models/extraction",
          "Llama 3.1 8B (Base)": "accounts/fireworks/models/llama-v3p1-8b-instruct"}

filename_to_url_map = {
    "ko-20191231/a2019123110-k_htm.xml_context_FD2019Q4YTD": "https://www.sec.gov/Archives/edgar/data/21344/000002134420000006/a2019123110-k.htm",
    "ko-20191231/a2019123110-k_htm.xml_context_FI2019Q4": "https://www.sec.gov/Archives/edgar/data/21344/000002134420000006/a2019123110-k.htm",
    "vz-20211231/vz-20211231_htm.xml_context_ic5e77757e0a24b939213c7a6db0ec708_I20211231": "https://www.sec.gov/Archives/edgar/data/732712/000073271222000008/vz-20211231.htm",
    "vz-20211231/vz-20211231_htm.xml_context_i3d39a7697cb04f7e9918324e8c91597b_D20210101-20211231": "https://www.sec.gov/Archives/edgar/data/732712/000073271222000008/vz-20211231.htm",
    "cvx-20191231/cvx12312019-10kdoc_htm.xml_context_FI2019Q4": "https://www.sec.gov/Archives/edgar/data/93410/000009341020000010/cvx12312019-10kdoc.htm",
    "cvx-20191231/cvx12312019-10kdoc_htm.xml_context_FD2019Q4YTD": "https://www.sec.gov/Archives/edgar/data/93410/000009341020000010/cvx12312019-10kdoc.htm",
    "crm-20230131/crm-20230131_htm.xml_context_ib41f5e45110a4b88b9616fd4fdb14e1b_D20220201-20230131": "https://www.sec.gov/Archives/edgar/data/1108524/000110852423000011/crm-20230131.htm",
    "nke-20230531/nke-20230531_htm.xml_context_c-9": "https://www.sec.gov/Archives/edgar/data/320187/000032018723000039/nke-20230531.htm",
    "nke-20230531/nke-20230531_htm.xml_context_c-1": "https://www.sec.gov/Archives/edgar/data/320187/000032018723000039/nke-20230531.htm",
    "jnj-20231231/jnj-20231231_htm.xml_context_c-1": "https://www.sec.gov/Archives/edgar/data/200406/000020040624000013/jnj-20231231.htm",
    "hd-20220130/hd-20220130_htm.xml_context_idf940048cc7f40e1a2d9df6651b878f3_D20210201-20220130": "https://www.sec.gov/Archives/edgar/data/354950/000035495022000070/hd-20220130.htm",
    "hd-20220130/hd-20220130_htm.xml_context_i343219cd57134c0b9e87fd1dfae85e84_I20220130": "https://www.sec.gov/Archives/edgar/data/354950/000035495022000070/hd-20220130.htm",
    "ba-20211231/ba-20211231_htm.xml_context_i11e13974becf4d89b786a672e97982a0_I20211231": "https://www.sec.gov/Archives/edgar/data/12927/000001292722000010/ba-20211231.htm",
    "ba-20211231/ba-20211231_htm.xml_context_i6d361a861ed840de8f571199b7bf9359_D20210101-20211231": "https://www.sec.gov/Archives/edgar/data/12927/000001292722000010/ba-20211231.htm"
}

with open('finer_example.json') as f:
    tagging_example = json.load(f)


def inference(inputs: str, model, max_new_token=75, delimiter="\n", if_print_out=False):
    config = 0
    try:
        config = dotenv.dotenv_values(".env")['FIREWORKS_KEY']
    except:
        try:
            config = os.getenv('FIREWORKS_KEY')
        except:
            pass

    client = Fireworks(api_key=config)
    response = client.chat.completions.create(
        model=model,
        max_tokens=max_new_token,
        messages=[
            {
                "role": "user",
                "content": inputs
            }
        ],
        temperature=0.0,
        stream=False
    )
    answer = (response.choices[0].message.content)
    # print(answer)
    return answer


def get_generic_ui(task_info):
    with gr.Blocks() as ui:
        gr.Markdown(
            f"""
{task_info['description']}
### Usage
* **Input:** {task_info['input']}.
* **Output:** {task_info['output']}. 

            """
        )
        gr.Interface(
            fn=process_generic,
            cache_examples=False,
            inputs=[
                gr.Textbox(label="Question"), gr.Textbox(label="GT Answer"), task_info['model']
            ],
            outputs=[
                gr.HTML(label="Llama 3.1 8b (Base) output"),
                gr.HTML(label="Llama 3.1 8b (fine-tuned) output"),
                gr.HTML(label="Ground truth answer")
            ],
            examples=task_info['examples'],
            examples_per_page=20,
            flagging_mode="never"

        )
    return ui


def process_generic(question, gt, ft_model):
    global extraction_data
    result = [[], []]
    context = question
    ft_model = "accounts/d0nnw0n9-c1910b/models/" + ft_model
    print(ft_model)
    for i, model in enumerate(
            ["accounts/fireworks/models/llama-v3p1-8b-instruct", ft_model]):
        output = inference(context, model)
        result[i] = output.split("<|end_of_text|>")[0]

    all_results = [result[0], result[1], gt]
    model_names = ["Llama 3.1 8b (Base) output", "Llama 3.1 8b (fine-tuned) output",
                   "Ground truth answer"]

    return tuple(all_results)


def process_extract(question, file):
    global extraction_data
    if file not in extraction_data:
        raise gr.Error("This XBRL file does not exist. Please select a valid file name from the examples", duration=5)

    if question in extraction_data[file]:
        gt_answer = extraction_data[file][question]['target']
        context = extraction_data[file][question]['context'].replace("QQQQQ", question)
    else:
        gt_answer = None
        context = list(extraction_data[file].values())[0]['context'].replace("QQQQQ", question)

    result = [[], []]
    for i, model in enumerate(
            ["accounts/fireworks/models/llama-v3p1-8b-instruct", "accounts/d0nnw0n9-c1910b/models/extraction"]):
        output = inference(context, model)
        result[i] = output.split("<|end_of_text|>")[0]

    all_results = [result[0], result[1], gt_answer]
    model_names = ["Llama 3.1 8b (Base) output", "Llama 3.1 8b (fine-tuned for XBRL extraction) output",
                   "Ground truth answer"]
    for i, x in enumerate(all_results):
        all_results[i] = process_html(x, file, model_names[i])

    return tuple(all_results)


def process_html(formula_str, report_url, model_name):
    """
    Converts a formula string into an HTML string with numbers linked to a report URL
    using Text Fragments. Numbers in the link are formatted with commas.
    """
    if not formula_str or not isinstance(formula_str, str) or not report_url:
        return formula_str if isinstance(formula_str, str) else ""

    def replace_number_with_link(match):
        number_str = match.group(0)
        search_text = number_str

        try:
            val = int(number_str)
            search_text = format(val, ',')
            search_text = search_text.replace(',000,000', '')
        except ValueError:
            pass  # search_text remains number_str

        url_encoded_search_text = quote(search_text)
        report_url_correct = filename_to_url_map[report_url]
        # Display the original number from the formula as the link text
        return f'''
        <a href="{report_url_correct}#:~:text={url_encoded_search_text}" target="_blank" 
        style="cursor: pointer; padding: 3px 5px; border-radius: 4px; background-color: var(--color-green-200); color:var(--color-green-800) ">{number_str}</a>'''

    # Regex to find whole numbers. \b ensures matching whole numbers only.
    # If your formulas can contain decimal numbers that also need linking (e.g., "3.14"),
    # you could use a regex like r'\b\d+\.?\d*\b'.
    # For "(500000 / 584000) * 100", r'\b\d+\b' is sufficient.
    html_output = re.sub(r'\b\d+\b', replace_number_with_link, formula_str)
    html_output = f'''
    
    <div id="component-22" class="block svelte-11xb1hd padded auto-margin" style="border-style: solid; overflow: hidden; min-width: min(160px, 100%); border-width: var(--block-border-width);"> 
    <label class="svelte-173056l container show_textbox_border"> <span data-testid="block-info" class="svelte-1gfkn6j" style="color:var(--primary-500)">{model_name}</span>  
    <div class="input-container svelte-173056l">
    <div     style="box-shadow: var(--input-shadow), padding: 12px 0 !important;">
        {html_output}
    </div>  
    </div></label> 
    </div>'''
    return html_output


def process_tagging(sentence):
    numbers = re.findall(r'\b\d+\.?\d*\b', sentence)
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]

    extracted_numbers = []
    for num_str in numbers:
        if num_str in [str(x) for x in list(range(2000, 2025, 1))]:
            continue

        # Exclude 1 or 2 digit numbers followed by a comma and then a 4 digit number (likely day and year)
        match = re.search(rf"{re.escape(num_str)}\s*,\s*\d{{4}}", sentence)
        if match:
            continue

        # Exclude numbers followed by a month
        match = re.search(rf"{re.escape(num_str)}\s+({'|'.join(months)})", sentence, re.IGNORECASE)
        if match:
            continue

        extracted_numbers.append(num_str)
    print(extracted_numbers)

    result = [[], []]

    for i, model in enumerate(
            ["accounts/fireworks/models/llama-v3p1-8b-instruct", "accounts/d0nnw0n9-c1910b/models/finer"]):
        for x in extracted_numbers:
            prompt = f'''What is the appropriate XBRL US GAAP tag for "{x}" in the given sentence? Output the US GAAP tag only and nothing else. \n "{sentence}"\n'''
            output = inference(prompt, model)
            output = output.split("<|end_of_text|>")[0]
            result[i].append([x, output])

    gt = None
    if sentence in tagging_example:
        gt = tagging_example[sentence]
    return result[0], result[1], gt
