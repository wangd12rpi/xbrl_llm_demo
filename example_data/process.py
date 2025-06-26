import json
import glob
import os

def process_jsonl_files():
    """
    Process JSONL files in the current directory:
    1. For regular task files: take top 50 examples and convert format
    2. For sentiment files: take top 50 from each, merge all into one file
    """
    
    # Get all JSONL files in current directory
    jsonl_files = glob.glob("*.jsonl")
    
    # Sentiment task files to be merged
    sentiment_files = ['fiqa_test.jsonl', 'fpb_test.jsonl', 'nwgi_test.jsonl', 'tfns_test.jsonl']
    
    # Collect sentiment data
    sentiment_data = []
    
    for jsonl_file in jsonl_files:
        print(f"Processing {jsonl_file}...")
        
        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Parse JSON lines
            data = []
            for line in lines:
                line = line.strip()
                if line:
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        print(f"Error parsing line in {jsonl_file}: {e}")
                        continue
            
            if jsonl_file in sentiment_files:
                # Take top 50 from this sentiment file and add to sentiment collection
                top_50_sentiment = data[:50]
                for item in top_50_sentiment:
                    converted_item = {
                        item.get("context", ""): item.get("target", "")
                    }
                    sentiment_data.append(converted_item)
                print(f"Added top {len(top_50_sentiment)} items from {jsonl_file} to sentiment collection")
            
            else:
                # Process regular task files
                # Extract task name from filename (remove _test.jsonl)
                task_name = jsonl_file.replace('_test.jsonl', '')
                
                # Take top 50 examples
                top_50 = data[:50]
                
                # Convert format from {"context": ..., "target": ...} to {"question": "answer"}
                converted_data = []
                for item in top_50:
                    converted_item = {
                        item.get("context", ""): item.get("target", "")
                    }
                    converted_data.append(converted_item)
                
                # Write to new file
                output_file = f"{task_name}_example.jsonl"
                with open(output_file, 'w', encoding='utf-8') as f:
                    for item in converted_data:
                        f.write(json.dumps(item, ensure_ascii=False) + '\n')
                
                print(f"Created {output_file} with {len(converted_data)} examples")
        
        except FileNotFoundError:
            print(f"File {jsonl_file} not found")
        except Exception as e:
            print(f"Error processing {jsonl_file}: {e}")
    
    # Write sentiment data to combined file
    if sentiment_data:
        with open('sentiment_example.jsonl', 'w', encoding='utf-8') as f:
            for item in sentiment_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        print(f"Created sentiment_example.jsonl with {len(sentiment_data)} examples from {len(sentiment_files)} files (top 50 from each)")

if __name__ == "__main__":
    process_jsonl_files()