from llama_index import VectorStoreIndex, StorageContext, ServiceContext
from llama_index.chat_engine.types import ChatMode
from llama_index.llms import OpenAI
from llama_index.llms.openai_utils import ALL_AVAILABLE_MODELS, CHAT_MODELS
from llama_index.vector_stores import MilvusVectorStore
import openai
import gradio as gr
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY", "sk-123456789012345678901234567890123456789012345678")
# original base is "https://api.openai.com/v1"
openai.api_base = os.environ.get("OPENAI_API_BASE", "http://milvus-openai:8000/")

model = os.environ.get("MODEL", "/models/mistral-7b-v0.1.Q6_K.gguf")
# https://docs.llamaindex.ai/en/stable/examples/chat_engine/chat_engine_openai.html
# and then, of course, my model running on llama.cpp isn't supported... so we have to hack
ALL_AVAILABLE_MODELS[model] = 4096
CHAT_MODELS[model] = 4096
service_context = ServiceContext.from_defaults(llm=OpenAI(model=model))

vector_store = MilvusVectorStore(
    host=os.environ.get("MILVUS_HOST", "milvus-standalone"),
    port=os.environ.get("MILVUS_PORT", "19530"),
    collection_name="webscrape",
    # this took a while to sort out and wasn't obvious
    # the sliding window of Mistral is 4096*32, and this seemed to work
    dim=4096,
    service_context=service_context
)
index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
query_engine = index.as_chat_engine(chat_mode=ChatMode.OPENAI, verbose=True)


# index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
# query_engine = index.as_query_engine()

def chatbot(input_text):
    print("entering chatbot")

    if input_text == 'reset':
        query_engine.reset()
        r = "ok"
    else:
        print(f"input text: {input_text}")
        response = query_engine.chat(input_text)
        # response = query_engine.query(input_text)
        print(f"response: {response}")
        r = response.response
    return r


# gr.ChatInterface(
#     chatbot,
#     chatbot=gr.Chatbot(height=300),
#     textbox=gr.Textbox(placeholder="Ask me a yes or no question", container=False, scale=7),
#     title="Yes Man",
#     description="Ask Yes Man any question",
#     theme="soft",
#     examples=["Hello", "Am I cool?", "Are tomatoes vegetables?"],
#     cache_examples=True,
#     retry_btn=None,
#     undo_btn="Delete Previous",
#     clear_btn="Clear",
# ).launch(share=True)

iface = gr.Interface(fn=chatbot,
                     inputs=gr.Textbox(lines=7, label="Enter your text"),
                     outputs="text",
                     title="Sample Content Querying")

iface.launch(share=True, server_port=8000, server_name="0.0.0.0")
