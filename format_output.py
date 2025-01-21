import json

# Read your existing JSONL file
input_file_path = "./static/fine_tune/leetcode_solution.jsonl"
output_file_path = "./static/fine_tune/leetcode_solution_formatted.jsonl"

with open(input_file_path, 'r') as infile, open(output_file_path, 'w') as outfile:
    for line in infile:
        data = json.loads(line)
        formatted_data = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that explains coding problems and provides solutions."},
                {"role": "user", "content": data["prompt"]},
                {"role": "assistant", "content": data["completion"]}
            ]
        }
        outfile.write(json.dumps(formatted_data) + "\n")
