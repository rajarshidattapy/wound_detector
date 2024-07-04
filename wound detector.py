import google.generativeai as genai
from pathlib import Path
import gradio as gr

# Set up the model
generation_config = {
  "temperature": 0,
  "top_p": 1,
  "top_k": 32,
  "max_output_tokens": 4096,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  }
]

genai.configure(api_key = "API key")

model = genai.GenerativeModel(model_name = "gemini-pro-vision",
                              generation_config = generation_config,
                              safety_settings = safety_settings)

def input_image_setup(file_loc):
    if not (img := Path(file_loc)).exists():
        raise FileNotFoundError(f"Could not find image: {img}")

    image_parts = [
        {
            "mime_type": "image/jpeg",
            "data": Path(file_loc).read_bytes()
            }
        ]
    return image_parts

def generate_gemini_response(input_prompt,text_input, image_loc):

    image_prompt = input_image_setup(image_loc)
    prompt_parts = [input_prompt + text_input ,image_prompt[0]]
    response = model.generate_content(prompt_parts)
    return response.text

#input_prompt = """ This image shows a person with an  injury or the visible symptoms on the body.  Please analyze the image and the prompted message and identify the possible injury. Based on your analysis, suggest appropriate first aid measures that can be taken to address the injury. """

input_prompt = """ This image shows a person with an injury or visible symptoms on the body.
Please analyze the image along with  the prompted message and identify the possible injury.
Based on your analysis, suggest appropriate first aid measures that can be taken to address the injury.
And also provides useful website links (Indian links only) which are valid and existing
and which can give more information regarding the first aid for the injury and also
Ensure the target website links are publicly accessible and not blocked by firewalls or login requirements.
And also provide contact information of the helpline for the next steps. And constrain the response to India. 
The prompted message is  """ 

def upload_file(files, text_input):  # Added text_input parameter
    file_paths = [file.name for file in files]
    if file_paths:
        response = generate_gemini_response(input_prompt,text_input, file_paths[0])  # Pass text_input
    return file_paths[0], response

with gr.Blocks() as demo:
    header = gr.Label("Please let us know about your injury and gen ai will try to help you to find the best first aid:")
    text_input = gr.Textbox(label="Explain a bit more about your injury")  # New text box
    image_output = gr.Image()
    upload_button = gr.UploadButton("Click to upload an image of the injury",
                                    file_types=["image"],
                                    file_count="multiple")

    file_output = gr.Textbox(label="First Aid process")
    combined_output = [image_output, file_output]

    upload_button.upload(upload_file, [upload_button, text_input], combined_output)  # Pass text_input

demo.launch(debug=True)
