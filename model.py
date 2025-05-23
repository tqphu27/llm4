#model_marketplace.config
# {"token_length": "4018", "accuracy": "70", "precision": "fp16", "sampling_frequency:": "44100", "mono": true, "fps": "74", "resolution": "480", "image_width": "1080", "image_height": "1920", "framework": "transformers", "dataset_format": "llm", "dataset_sample": "[id on s3]", "weights": [
#     {
#       "name": "DeepSeek-V3",
#       "value": "deepseek-ai/DeepSeek-V3",
#       "size": 20,
#       "paramasters": "685B",
#       "tflops": 14, 
#       "vram": 20,
#       "nodes": 10
#     },
# {
#       "name": "DeepSeek-V3-bf16",
#       "value": "opensourcerelease/DeepSeek-V3-bf16",
#       "size": 1500,
#       "paramasters": "684B",
#       "tflops": 80, 
#       "vram": 48,
#       "nodes": 10
#     }
#   ], "cuda": "11.4", "task":["text-generation", "text-classification", "text-summarization", "text-ner", "question-answering"]}

# import math
# import pathlib
# import random
import subprocess
import time
# from typing import List, Dict, Optional
# import accelerate
from aixblock_ml.model import AIxBlockMLBase
import torch
from transformers import pipeline
import os
from huggingface_hub import HfFolder
import wandb
from prompt import qa_with_context, text_classification, text_summarization, qa_without_context,text_ner,chatbot_with_history
import zipfile

# Đặt token của bạn vào đây
hf_token = os.getenv("HF_TOKEN", "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")
# Lưu token vào local
HfFolder.save_token(hf_token)
# wandb.login('allow',"69b9681e7dc41d211e8c93a3ba9a6fb8d781404a")
# print("Login successful")
from huggingface_hub import login 
hf_access_token = "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"
login(token = hf_access_token)
CUDA_VISIBLE_DEVICES=[]
for i in range(torch.cuda.device_count()):
    CUDA_VISIBLE_DEVICES.append(i)
os.environ['CUDA_VISIBLE_DEVICES'] = ','.join(f'{i}' for i in range(len(CUDA_VISIBLE_DEVICES) ))
print(os.environ['CUDA_VISIBLE_DEVICES'])

if torch.cuda.is_available():
    if torch.cuda.is_bf16_supported():
        dtype = torch.bfloat16
    else:
        dtype = torch.float16

    print("CUDA is available.")
    
    _model = pipeline(
        "text-generation",
        model="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B", 
        torch_dtype=dtype, 
        device_map="auto",  # Hoặc có thể thử "cpu" nếu không ổn,
        max_new_tokens=256,
        token = "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"
    )
else:
    print("No GPU available, using CPU.")
    _model = pipeline(
        "text-generation",
        model="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B", 
        device_map="cpu",
        max_new_tokens=256,
        token = "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"
    )

# from typing import List, Dict, Optional
from aixblock_ml.model import AIxBlockMLBase
# import torch.distributed as dist
import os
import torch
import os
import subprocess
import random
# import asyncio
# import logging
import logging
import subprocess
# import threading
import time
# import base64
import json

from logging_class import start_queue, write_log
 

HOST_NAME = os.environ.get('HOST_NAME',"https://dev-us-west-1.aixblock.io")
TYPE_ENV = os.environ.get('TYPE_ENV',"DETECTION")
import requests
from function_ml import connect_project, download_dataset, upload_checkpoint
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("aixblock-mcp")

# def download_dataset(data_zip_dir, project_id, dataset_id, token):
#     # data_zip_path = os.path.join(data_zip_dir, "data.zip")
#     url = f"{HOST_NAME}/api/dataset_model_marketplace/download/{dataset_id}?project_id={project_id}"
#     print(url)
#     payload = {}
#     headers = {
#         'accept': 'application/json',
#         'Authorization': f'Token {token}'
#     }

#     response = requests.request("GET", url, headers=headers, data=payload)
#     dataset_name = response.headers.get('X-Dataset-Name')
#     if response.status_code == 200:
#         with open(data_zip_dir, 'wb') as f:
#             f.write(response.content)
#         return dataset_name
#     else:
#         return None

# def upload_checkpoint(checkpoint_model_dir, project_id, token, path_file, version, send_mail=False):
#     import os
#     url = f"{HOST_NAME}/api/checkpoint_model_marketplace/upload/"

#     payload = {
#         "type_checkpoint": "ml_checkpoint",
#         "project_id": f'{project_id}',
#         "is_training": send_mail,
#         "full_path": path_file,
#         "version": version
#     }
#     headers = {
#         'accept': 'application/json',
#         'Authorization': f'Token {token}'
#     }

#     checkpoint_name = None

#     # response = requests.request("POST", url, headers=headers, data=payload) 
#     with open(checkpoint_model_dir, 'rb') as file:
#         files = {'file': file}
#         response = requests.post(url, headers=headers, files=files, data=payload)
#         checkpoint_name = response.headers.get('X-Checkpoint-Name')

#     print("upload done")
#     return checkpoint_name
import uuid
CHANNEL_STATUS = {}
class MyModel(AIxBlockMLBase):

    # def predict(self, tasks: List[Dict], context: Optional[Dict] = None, **kwargs) -> List[Dict]:
    #     """ 
    #     """
    #     print(f'''\
    #     Run prediction on {tasks}
    #     Received context: {context}
    #     Project ID: {self.project_id}
    #     Label config: {self.label_config}
    #     Parsed JSON Label config: {self.parsed_label_config}''')
    #     return []

    # def fit(self, event, data, **kwargs):
    #     old_data = self.get('my_data')
    #     old_model_version = self.get('model_version')
    #     print(f'Old data: {old_data}')
    #     print(f'Old model version: {old_model_version}')

    #     # store new data to the cache
    #     self.set('my_data', 'my_new_data_value')
    #     self.set('model_version', 'my_new_model_version')
    #     print(f'New data: {self.get("my_data")}')
    #     print(f'New model version: {self.get("model_version")}')

    #     print('fit() completed successfully.')
    @mcp.tool()
    def action(self,  command,**kwargs):
        
        print(f"""
                command: {command}
              """)
        
        if command.lower() == "train":
                import threading
                import os

                model_id = kwargs.get("model_id", "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B")  #"tiiuae/falcon-7b" "bigscience/bloomz-1b7" `zanchat/falcon-1b` `appvoid/llama-3-1b` deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B` `mistralai/Mistral-7B-v0.1` `bigscience/bloomz-1b7` `Qwen/Qwen2-1.5B`
                dataset_id = kwargs.get("dataset_id","timdettmers/openassistant-guanaco") #gingdev/llama_vi_52k kigner/ruozhiba-llama3-tt

                push_to_hub = kwargs.get("push_to_hub", True)
                hf_model_id = kwargs.get("hf_model_id", "deepseek-r1-4b")
                push_to_hub_token = kwargs.get("push_to_hub_token", "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")

                task = kwargs.get("task", "text-generation")
                framework = kwargs.get("framework", "huggingface")
                prompt = kwargs.get("prompt", "")
                report_to = kwargs.get("report_to", "tensorboard")
                wantdb_api_key = kwargs.get("wantdb_api_key", "69b9681e7dc41d211e8c93a3ba9a6fb8d781404a")
                trainingArguments = kwargs.get("TrainingArguments", None)
                cuda_debug = kwargs.get("cuda_debug", False)

                json_file = "training_args.json"
                absolute_path = os.path.abspath(json_file)

                with open(absolute_path, 'w') as f:
                    json.dump(trainingArguments, f)
                # https://gist.github.com/TengdaHan/1dd10d335c7ca6f13810fff41e809904
                print(trainingArguments)
                if len(wantdb_api_key)> 0 and wantdb_api_key != "69b9681e7dc41d211e8c93a3ba9a6fb8d781404a":
                    wandb.login('allow',wantdb_api_key)
                
                if cuda_debug == True:
                    os.environ['NCCL_DEBUG_SUBSYS'] ='ALL'
                    os.environ['NCCL_DEBUG'] ='INFO'
                #     os.environ['CUDA_LAUNCH_BLOCKING']="1"
                #     os.environ['TORCH_USE_CUDA_DSA'] = "1"
                # else:
                   
                os.environ['CUDA_LAUNCH_BLOCKING']="0"
                os.environ['TORCH_USE_CUDA_DSA'] = "0"
                clone_dir = os.path.join(os.getcwd())
                # epochs = kwargs.get("num_epochs", 10)
                project_id = kwargs.get("project_id",0)
                token = kwargs.get("token","ebcf0ceda01518700f41dfa234b6f4aaea0b57af")
                checkpoint_version = kwargs.get("checkpoint_version")
                checkpoint_id = kwargs.get("checkpoint")
                dataset_version = kwargs.get("dataset_version")
                dataset_id = kwargs.get("dataset")
                channel_log = kwargs.get("channel_log", "training_logs")
                world_size = kwargs.get("world_size", 1)
                rank = kwargs.get("rank", 0)
                master_add = kwargs.get("master_add","127.0.0.1")
                master_port = kwargs.get("master_port", "23456")
                # entry_file = kwargs.get("entry_file")
                configs = kwargs.get("configs")
                host_name = kwargs.get("host_name",HOST_NAME)
            
                host_name = "https://dev-us-west-1.aixblock.io"
                token = "ebcf0ceda01518700f41dfa234b6f4aaea0b57af"
                
                log_queue, logging_thread = start_queue(channel_log)
                write_log(log_queue)

                channel_name = f"{hf_model_id}_{str(uuid.uuid4())[:8]}"
                username = ""
                hf_model_name = ""

                try:
                    headers = {"Authorization": f"Bearer {push_to_hub_token}"}
                    response = requests.get("https://huggingface.co/api/whoami-v2", headers=headers)

                    if response.status_code == 200:
                        data = response.json()
                        username = data.get("name")
                        hf_model_name = f"{username}/{hf_model_id}"
                        print(f"Username: {username}")
                    else:
                        print(f"Error: {response.status_code} - {response.text}")
                        hf_model_name = "Token not correct"
                except Exception as e:
                    hf_model_name = "Token not correct"
                    print(e)

        
                # Đặt trạng thái kênh là "training"
                CHANNEL_STATUS[channel_name] = {
                        "status": "training",
                        "hf_model_id": hf_model_name,
                        "command": command,
                        "created_at": time.time()
                    }
                print(f"🚀 Đã bắt đầu training kênh: {channel_name}")

                # hyperparameter = kwargs.get("hyperparameter")

                # !pip install nvidia-ml-py
                # from pynvml import *
                # nvmlInit()
                # print(f"Driver Version: {nvmlSystemGetDriverVersion()}")
                # # Driver Version: 11.515.48
                # deviceCount = nvmlDeviceGetCount()
                # for i in range(deviceCount):
                # handle = nvmlDeviceGetHandleByIndex(i)
                # print(f"Device {i} : {nvmlDeviceGetName(handle)}")
                # nvmlShutdown()

                def func_train_model(clone_dir, project_id, token, checkpoint_version, checkpoint_id, dataset_version, dataset_id,model_id,world_size,rank,master_add,master_port,prompt, json_file, channel_log, hf_model_id, push_to_hub, push_to_hub_token,host_name):
                    # from misc import get_device_counts
                    import os
                    dataset_path = None
                    project = connect_project(host_name, token, project_id)

                    if dataset_version and dataset_id and project:
                        dataset_path = os.path.join(clone_dir, f"datasets/{dataset_version}")

                        if not os.path.exists(dataset_path):
                            data_path = os.path.join(clone_dir, "data_zip")
                            os.makedirs(data_path, exist_ok=True)
                            # data_zip_dir = os.path.join(clone_dir, "data_zip/data.zip")
                            # dataset_name = download_dataset(data_zip_dir, project_id, dataset_id, token)
                            dataset_name = download_dataset(project, dataset_id, data_path)
                            print(dataset_name)
                            if dataset_name: 
                                data_zip_dir = os.path.join(data_path, dataset_name)

                                # Giải nén file đầu tiên
                                with zipfile.ZipFile(data_zip_dir, 'r') as zip_ref:
                                    zip_ref.extractall(dataset_path)

                                # Kiểm tra nếu trong dataset_path chỉ có 1 file zip => giải nén tiếp
                                extracted_files = os.listdir(dataset_path)
                                zip_files = [f for f in extracted_files if f.endswith('.zip')]

                                if len(zip_files) == 1:
                                    inner_zip_path = os.path.join(dataset_path, zip_files[0])
                                    print(f"🔁 Found inner zip file: {inner_zip_path}, extracting...")
                                    with zipfile.ZipFile(inner_zip_path, 'r') as inner_zip:
                                        inner_zip.extractall(dataset_path)
                                    os.remove(inner_zip_path)

                    import torch
                    # https://huggingface.co/docs/accelerate/en/basic_tutorials/launch
                    # https://huggingface.co/docs/accelerate/en/package_reference/cli
                    subprocess.run(
                                (
                                    "whereis accelerate"
                                ),
                                shell=True,
                            )
                    print("===Train===")
                    # https://github.com/huggingface/accelerate/issues/1474
                    if framework == "huggingface" or framework == "transformers":
                        if int(world_size) > 1:
                            if int(rank) == 0:
                                print("master node")
                                #  --dynamo_backend 'no' \
                                # --rdzv_backend c10d
                                command = (
                                        "venv/bin/accelerate launch --num_processes {num_processes} --num_machines {SLURM_NNODES} --machine_rank 0 --main_process_ip {head_node_ip} --main_process_port {port} {file_name} --training_args_json {json_file} --dataset_local {dataset_path} --channel_log {channel_log} --hf_model_id {hf_model_id} --push_to_hub {push_to_hub} --push_to_hub_token {push_to_hub_token} --model_id {model_id}"
                                    ).format(
                                        num_processes=world_size*torch.cuda.device_count(),
                                        SLURM_NNODES=world_size,
                                        head_node_ip=master_add,
                                        port=master_port,
                                        file_name="./run_distributed_accelerate.py", 
                                        json_file=json_file,
                                        dataset_path=dataset_path,
                                        channel_log=channel_log,
                                        hf_model_id=hf_model_id,
                                        push_to_hub=push_to_hub,
                                        model_id=model_id,
                                        push_to_hub_token=push_to_hub_token
                                    )
                                process = subprocess.run(
                                    command,
                                    shell=True,
                                    # capture_output=True, text=True).stdout.strip("\n")
                                )
                                #print(process)
                                # run_train(command)
                            else:
                                print("worker node")
                                # --rdzv_backend c10d
                                command = (
                                        "venv/bin/accelerate launch --num_processes {num_processes} --num_machines {SLURM_NNODES} --machine_rank {machine_rank} --main_process_ip {head_node_ip} --main_process_port {port} {file_name} --training_args_json {json_file} --dataset_local {dataset_path} --channel_log {channel_log} --hf_model_id {hf_model_id} --push_to_hub {push_to_hub} --push_to_hub_token {push_to_hub_token} --model_id {model_id}"
                                    ).format(
                                        num_processes=world_size*torch.cuda.device_count(),
                                        SLURM_NNODES=world_size,
                                        head_node_ip=master_add,
                                        port=master_port,
                                        machine_rank=rank,
                                        file_name="./run_distributed_accelerate.py", 
                                        json_file=json_file,
                                        dataset_path=dataset_path,
                                        channel_log=channel_log,
                                        hf_model_id=hf_model_id,
                                        push_to_hub=push_to_hub,
                                        model_id=model_id,
                                        push_to_hub_token=push_to_hub_token
                                    )
                                process = subprocess.run(
                                    command,
                                    shell=True,
                                    # capture_output=True, text=True).stdout.strip("\n")
                                )
                                #print(process)
                                # run_train(command)
                        else:
                            if torch.cuda.device_count() > 1: # multi gpu
                                            #                                     --rdzv_backend c10d \
                                            # --main_process_ip {head_node_ip} \
                                            # --main_process_port {port} \
                                            # --mixed_precision 'fp16' \
                                            # --num_machines {SLURM_NNODES} \
                                            # --num_processes {num_processes}
                                command = (
                                        "venv/bin/accelerate launch --multi_gpu --num_machines {SLURM_NNODES} --machine_rank 0 --num_processes {num_processes} {file_name} --training_args_json {json_file}  --dataset_local {dataset_path} --channel_log {channel_log} --hf_model_id {hf_model_id} --push_to_hub {push_to_hub} --push_to_hub_token {push_to_hub_token} --model_id {model_id}"
                                    ).format(
                                        num_processes=world_size*torch.cuda.device_count(),
                                        SLURM_NNODES=world_size,
                                        # head_node_ip=os.environ.get("head_node_ip", master_add),
                                        port=master_port,
                                        file_name="./run_distributed_accelerate.py", 
                                        json_file=json_file,
                                        dataset_path=dataset_path,
                                        channel_log=channel_log,
                                        hf_model_id=hf_model_id,
                                        push_to_hub=push_to_hub,
                                        model_id=model_id,
                                        push_to_hub_token=push_to_hub_token
                                    )
                                print("================2")
                                print(command)
                                print("================2")
                                process = subprocess.run(
                                    command,
                                    shell=True
                                )
                                process = subprocess.run(
                                    command
                                )
                                #print(process)
                                # run_train(command)
                                # mixed_precision: fp16
                            elif torch.cuda.device_count() == 1: # one gpu
                                # num_processes = world_size*get_device_count()
                                #    --rdzv_backend c10d \
                                #     --main_process_ip {head_node_ip} \
                                #     --main_process_port {port} \
                                # --num_cpu_threads_per_process=2 --num_processes {num_processes} \
                                #     --num_machines {SLURM_NNODES} \
                                command = (
                                    "venv/bin/accelerate launch {file_name} --training_args_json {json_file}  --dataset_local {dataset_path} --channel_log {channel_log} --hf_model_id {hf_model_id} --push_to_hub {push_to_hub} --push_to_hub_token {push_to_hub_token} --model_id {model_id}"
                                ).format(
                                    # num_processes=os.environ.get("num_processes", num_processes),
                                    # SLURM_NNODES=os.environ.get("SLURM_NNODES", world_size),
                                    # head_node_ip=os.environ.get("head_node_ip", master_add),
                                    # port=os.environ.get("port", master_port),
                                    file_name="./run_distributed_accelerate.py", 
                                    json_file=json_file,
                                    dataset_path=dataset_path,
                                    channel_log=channel_log,
                                    hf_model_id=hf_model_id,
                                    push_to_hub=push_to_hub,
                                    model_id=model_id,
                                    push_to_hub_token=push_to_hub_token
                                )
                                print("================")
                                print(command)
                                print("================")
                                process = subprocess.run(
                                    command,
                                    shell=True
                                )
                                #print(process)
                                # run_train(command)
                                # python3.10 -m pip install -r requirements.txt
                            else: # no gpu
                                command = (
                                        "venv/bin/accelerate launch --cpu {file_name} --training_args_json {json_file} --dataset_local {dataset_path} --channel_log {channel_log} --hf_model_id {hf_model_id} --push_to_hub {push_to_hub} --push_to_hub_token {push_to_hub_token} --model_id {model_id}"
                                    ).format(
                                        file_name="./run_distributed_accelerate.py", 
                                        json_file=json_file,
                                        dataset_path=dataset_path,
                                        channel_log=channel_log,
                                        hf_model_id=hf_model_id,
                                        push_to_hub=push_to_hub,
                                        model_id=model_id,
                                        push_to_hub_token=push_to_hub_token
                                    )
                                
                                process = subprocess.run(
                                    command,
                                    shell=True,
                                    # capture_output=True, text=True).stdout.strip("\n")
                                )
                                #print(process)
                                # run_train(command)

                    elif framework == "pytorch":
                        import torch
                        # from peft import AutoPeftModelForCausalLM
                        # from transformers import AutoTokenizer, pipeline
                        # from datasets import load_dataset
                        # from random import randint
                        # from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments #BitsAndBytesConfig,AutoConfig,
                        # from trl import SFTTrainer
                        # import pathlib
                        # from transformers import TrainerCallback
                        # import numpy as np
                        # from torch.utils.data.dataloader import DataLoader
                        # from transformers import DataCollatorWithPadding      
                        process = subprocess.run(
                                (
                                    "whereis torchrun"
                                ),
                                shell=True,
                            )
                        # print(process.stdout.replace("venv/bin/torchrun: ",""))
                        if int(world_size) > 1:
                            if rank == 0:
                                print("master node")
                                # args = f"--model_id {model_id} --dataset_id {dataset_id} --num_train_epochs {num_train_epochs} " \
                                #     f"--bf16 {bf16} --fp16 {fp16} --use_cpu {use_cpu} --push_to_hub {push_to_hub} " \
                                #     f"--hf_model_id {hf_model_id} --max_seq_length {max_seq_length} --framework {framework} " \
                                #     f"--per_device_train_batch_size {per_device_train_batch_size} --gradient_accumulation_steps {gradient_accumulation_steps} " \
                                #     f"--gradient_checkpointing {gradient_checkpointing} --optim {optim} --logging_steps {logging_steps} " \
                                #     f"--learning_rate {learning_rate} --max_grad_norm {max_grad_norm} --lora_alpha {lora_alpha} " \
                                #     f"--lora_dropout {lora_dropout} --bias {bias} --target_modules {target_modules} --task_type {task_type}"
                                #  --dynamo_backend 'no' \
                                command = (
                                        "venv/bin/torchrun --nnodes {nnodes} --node_rank {node_rank} --nproc_per_node {nproc_per_node} "
                                        "--master_addr {master_addr} --master_port {master_port} {file_name} --training_args_json {json_file} --dataset_local {dataset_path} --channel_log {channel_log} --hf_model_id {hf_model_id} --push_to_hub {push_to_hub} --push_to_hub_token {push_to_hub_token} --model_id {model_id}"
                                    ).format(
                                         nnodes=int(world_size),
                                        node_rank= int(rank),
                                        nproc_per_node=world_size*torch.cuda.device_count(),
                                        master_addr="127.0.0.1",
                                        master_port="23456",
                                        file_name="./run_distributed_accelerate.py",
                                        json_file=json_file,
                                        dataset_path=dataset_path,
                                        channel_log=channel_log,
                                        hf_model_id=hf_model_id,
                                        push_to_hub=push_to_hub,
                                        model_id=model_id,
                                        push_to_hub_token=push_to_hub_token
                                    )
                                process = subprocess.run(
                                    command,
                                    shell=True,
                                    # capture_output=True, text=True).stdout.strip("\n")
                                )
                                #print(process)
                                # run_train(command)
                            else:
                                print("worker node")
                                # args = f"--model_id {model_id} --dataset_id {dataset_id} --num_train_epochs {num_train_epochs} " \
                                #     f"--bf16 {bf16} --fp16 {fp16} --use_cpu {use_cpu} --push_to_hub {push_to_hub} " \
                                #     f"--hf_model_id {hf_model_id} --max_seq_length {max_seq_length} --framework {framework} " \
                                #     f"--per_device_train_batch_size {per_device_train_batch_size} --gradient_accumulation_steps {gradient_accumulation_steps} " \
                                #     f"--gradient_checkpointing {gradient_checkpointing} --optim {optim} --logging_steps {logging_steps} " \
                                #     f"--learning_rate {learning_rate} --max_grad_norm {max_grad_norm} --lora_alpha {lora_alpha} " \
                                #     f"--lora_dropout {lora_dropout} --bias {bias} --target_modules {target_modules} --task_type {task_type}"
                                command = (
                                        "venv/bin/torchrun --nnodes {nnodes} --node_rank {node_rank} --nproc_per_node {nproc_per_node} "
                                        "--master_addr {master_addr} --master_port {master_port} {file_name} --training_args_json {json_file} --dataset_local {dataset_path} --channel_log {channel_log} --hf_model_id {hf_model_id} --push_to_hub {push_to_hub} --push_to_hub_token {push_to_hub_token} --model_id {model_id}"
                                    ).format(
                                         nnodes=int(world_size),
                                       node_rank= int(rank),
                                        nproc_per_node=world_size*torch.cuda.device_count(),
                                        master_addr=master_add,
                                        master_port=master_port,
                                        file_name="./run_distributed_accelerate.py",
                                        json_file=json_file,
                                        dataset_path=dataset_path,
                                        channel_log=channel_log,
                                        hf_model_id=hf_model_id,
                                        push_to_hub=push_to_hub,
                                        model_id=model_id,
                                        push_to_hub_token=push_to_hub_token
                                    )
                                print(command)
                                process = subprocess.run(
                                    command,
                                    shell=True,
                                    # capture_output=True, text=True).stdout.strip("\n")
                                )
                                #print(process)
                                # run_train(command)
                        else:
                            command = (
                                        "venv/bin/torchrun --nnodes {nnodes} --node_rank {node_rank} --nproc_per_node {nproc_per_node} "
                                        "{file_name} --training_args_json {json_file} --dataset_local {dataset_path} --channel_log {channel_log} --hf_model_id {hf_model_id} --push_to_hub {push_to_hub} --push_to_hub_token {push_to_hub_token} --model_id {model_id}"
                                    ).format(
                                        nnodes=int(world_size),
                                        node_rank= int(rank),
                                        nproc_per_node=world_size*torch.cuda.device_count(),
                                        # master_addr=master_add,
                                        # master_port=master_port,
                                        file_name="./run_distributed_accelerate.py",
                                        json_file=json_file,
                                        dataset_path=dataset_path,
                                        channel_log=channel_log,
                                        hf_model_id=hf_model_id,
                                        push_to_hub=push_to_hub,
                                        model_id=model_id,
                                        push_to_hub_token=push_to_hub_token
                                    )
                            process = subprocess.run(
                                    command,
                                    shell=True,
                                    # capture_output=True, text=True).stdout.strip("\n")
                                )
                            
                                # run_train(command)
                    # else:
                    #         import torch
                    #         from peft import AutoPeftModelForCausalLM
                    #         from transformers import AutoTokenizer, pipeline
                    #         from datasets import load_dataset
                    #         from random import randint
                    #         from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments #BitsAndBytesConfig,AutoConfig,
                    #         from trl import SFTTrainer 
                    #         import pathlib
                    #         from transformers import TrainerCallback
                    #         import numpy as np
                    #         from torch.utils.data.dataloader import DataLoader
                    #         from transformers import DataCollatorWithPadding
                    #         # Hugging Face model id
                    #         if model_id == None:
                    #             model_id = "Qwen/Qwen2-1.5B" # or  `appvoid/llama-3-1b` tiiuae/falcon-7b` `mistralai/Mistral-7B-v0.1` `bigscience/bloomz-1b7` `Qwen/Qwen2-1.5B`
                    #         train_dataset = load_dataset(dataset_id, split="train")
                    #         # train_valid = train_dataset['train'].train_test_split(test_size=0.2)
                    #         # test_valid = train_dataset['test'].train_test_split(test_size=0.2)
                    #         # train_dataset = train_valid['train']
                    #         # test_dataset = test_valid['test']
                    #         # print(f"train_dataset: {train_dataset}")
                    #         # print(f"test_dataset: {test_dataset}")
                    
                    #         alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

                    #                         ### Instruction:
                    #                         {}

                    #                         ### Input:
                    #                         {}

                    #                         ### Response:
                    #                         {}"""
                    #         if len(prompt) > 0:
                    #              alpaca_prompt = prompt
                        
                    #         # def formatting_prompts_func(examples):
                    #         #     instructions = examples["instruction"]
                    #         #     inputs       = examples["input"]
                    #         #     outputs      = examples["output"]
                    #         #     texts = []
                    #         #     for instruction, input, output in zip(instructions, inputs, outputs):
                    #         #         text = alpaca_prompt.format(instruction, input, output) + EOS_TOKEN
                    #         #         texts.append(text)
                    #         #     return {"text": texts}
                    #         # def tokenizer_func(examples):
                    #         #     instructions = examples["instruction"]
                    #         #     inputs       = examples["input"]
                    #         #     outputs      = examples["output"]
                    #         #     texts = []
                    #         #     for instruction, input, output in zip(instructions, inputs, outputs):
                    #         #         text = alpaca_prompt.format(instruction, input, output) + EOS_TOKEN
                    #         #         texts.append(text)
                    #         #     return tokenizer("".join(texts),truncation=True, padding=True, max_length=128, return_tensors="pt")
                    #         #                 # examples follow format of resp json files
                    #         # train_dataset = train_dataset.map(tokenizer_func,remove_columns=train_dataset.column_names, batched=True)
                    #         # Load model and tokenizer
                    #         model = AutoModelForCausalLM.from_pretrained(
                    #             model_id,
                    #             device_map="auto",
                    #             low_cpu_mem_usage=True,
                    #             use_cache=True
                    #         )
                    #         tokenizer = AutoTokenizer.from_pretrained(model_id)
                    #         EOS_TOKEN = tokenizer.eos_token  # Must add EOS_TOKEN
                    #         tokenizer.add_special_tokens({'pad_token': '[PAD]'})
                    #         tokenizer.pad_token = tokenizer.eos_token
                    #         def preprocess_function(examples):  
                    #             instructions = examples["instruction"]
                    #             inputs       = examples["input"]
                    #             outputs      = examples["output"]
                    #             texts = []
                    #             for instruction, input, output in zip(instructions, inputs, outputs):
                    #                 text = alpaca_prompt.format(instruction, input, output) + EOS_TOKEN
                    #                 texts.append(text)
                    #             return tokenizer(texts,truncation=True, padding=True, max_length=128, return_tensors="pt")                         
                    #             # inputs = [ex['en'] for ex in examples['translation']]      
                    #             # targets = [ex['ru'] for ex in examples['translation']]
                    #             # model_inputs = tokenizer(inputs, text_target=targets, max_length=max_length, padding=True, truncation=True)
                    #         eval_dataset = train_dataset 
                    #         tokenized_datasets = train_dataset.map(
                    #             preprocess_function,
                    #             batched=True,
                    #             # remove_columns=train_dataset['train'].column_names,
                    #         )
                    #         # eval_tokenized_datasets = eval_dataset.map(
                    #         #     preprocess_function,
                    #         #     batched=True,
                    #         #     # remove_columns=train_dataset['train'].column_names,
                    #         # )

                    #         data_collator = DataCollatorWithPadding(tokenizer)
                    #         train_dataloader = DataLoader(train_dataset, shuffle=True, batch_size=16,collate_fn=data_collator)
                    #         eval_dataloader = DataLoader(eval_dataset, batch_size=16, collate_fn=data_collator)
                    #         # for epoch in range(2):
                    #         #     model.train()
                    #         #     for step, batch in enumerate(train_dataloader):          
                    #         #         outputs = model(**batch)
                    #         #         loss = outputs.loss
                    #         # print(len(train_dataset))
                    #         # print(len(eval_dataset))

                    #         with open(json_file, 'r') as f:
                    #             training_args_dict = json.load(f)

                    #         print("Data is formatted and ready!")
                            
                    #         # def compute_metrics(eval_pred):
                    #         #     predictions, labels = eval_pred
                    #         #     predictions = np.argmax(predictions, axis=1)
                    #         #     return accuracy.compute(predictions=predictions, references=labels)
                            
                    #         class TrainOnStartCallback(TrainerCallback):
                    #             def on_train_begin(self, args, state, control, logs=None, **kwargs):
                    #                 # Log training loss at step 0
                    #                 logs = logs or {}
                    #                 self.log(logs)

                    #             def log(self, logs):
                    #                 print(f"Logging at start: {logs}")

                    #         def is_valid_type(value, expected_type):
                    #             from typing import get_origin, get_args, Union
                    #             # Nếu không có type hint (Empty), chấp nhận giá trị
                    #             if expected_type is inspect._empty:
                    #                 return True
                    #             # Nếu type hint là generic (Union, Optional, List, etc.)
                    #             origin = get_origin(expected_type)
                    #             if origin is Union:  # Xử lý Union hoặc Optional
                    #                 return any(is_valid_type(value, arg) for arg in get_args(expected_type))
                    #             if origin is list:  # Xử lý List
                    #                 return isinstance(value, list) and all(is_valid_type(v, get_args(expected_type)[0]) for v in value)
                    #             if origin is dict:  # Xử lý Dict
                    #                 key_type, value_type = get_args(expected_type)
                    #                 return (
                    #                     isinstance(value, dict) and
                    #                     all(is_valid_type(k, key_type) for k in value.keys()) and
                    #                     all(is_valid_type(v, value_type) for v in value.values())
                    #                 )
                    #             # Kiểm tra kiểu cơ bản (int, float, str, etc.)
                    #             return isinstance(value, expected_type)


                    #         if training_args_dict:
                    #             import inspect
                    #             # Kết hợp dictionary từ JSON (nếu có) và giá trị mặc định
                    #             training_args_values = {**training_args_dict}

                    #             param_annotations = inspect.signature(TrainingArguments.__init__).parameters

                    #             valid_args = set(param_annotations.keys())
                    #             filtered_args = {k: v for k, v in training_args_values.items() if k in valid_args}

                    #             # Kiểm tra định dạng giá trị
                    #             validated_args = {}
                    #             for k, v in filtered_args.items():
                    #                 expected_type = param_annotations[k].annotation  # Lấy kiểu dữ liệu mong đợi
                    #                 if is_valid_type(v, expected_type):
                    #                     validated_args[k] = v
                    #                 else:
                    #                     print(f"Skipping invalid parameter: {k} (expected {expected_type}, got {type(v)})")

                    #             # Khởi tạo TrainingArguments với tham số đã được xác thực
                    #             training_args = TrainingArguments(**validated_args)

                    #         else:
                    #             training_args = TrainingArguments(
                    #                 output_dir= f"/app/data/checkpoint", # directory to save and repository id
                    #                 logging_dir= '/app/data/logs',
                    #                 learning_rate=2e-4,
                    #                 per_device_train_batch_size=3,
                    #                 per_device_eval_batch_size=16,
                    #                 num_train_epochs=10,
                    #                 weight_decay=0.01,
                    #                 save_strategy="epoch", 
                    #                 # report_to="tensorboard",
                    #                 report_to="wandb",
                    #                 use_cpu=False,
                    #                 bf16 = False,
                    #                 fp16 = False
                    #             )

                            
                    #         # https://github.com/huggingface/accelerate/issues/2618
                    #         # https://github.com/huggingface/huggingface-llama-recipes/blob/main/fine_tune/qlora_405B.slurm
                    #         # https://gist.github.com/rom1504/474f97a95a526d40ae44a3fc3c657a2e
                    #         # https://github.com/huggingface/accelerate/blob/main/examples/slurm/submit_multinode.sh
                    #         # https://github.com/huggingface/accelerate/blob/main/examples/slurm/submit_multigpu.sh
                    #         # https://github.com/huggingface/accelerate/blob/main/examples/slurm/submit_multinode_fsdp.sh
                    #         # https://github.com/huggingface/accelerate/blob/main/examples/slurm/submit_multicpu.sh
                    #         trainer = SFTTrainer(
                    #             dataset_text_field = "text",
                    #             model=model,
                    #             args=training_args,
                    #             train_dataset=tokenized_datasets,
                    #             # eval_dataset=eval_tokenized_datasets,
                    #             tokenizer=tokenizer,
                    #             # data_collator=data_collator,
                    #             # compute_metrics=compute_metrics,
                    #             dataset_kwargs={
                    #                                 "add_special_tokens": False,  # We template with special tokens
                    #                                 "append_concat_token": False, # No need to add additional separator token
                    #                                 'skip_prepare_dataset': True # skip the dataset preparation
                    #                             },
                    #             callbacks=[TrainOnStartCallback()]
                    #         )
                    #         # start training, the model will be automatically saved to the hub and the output directory
                    #         trainer.train()
                    #         # if push_to_hub == True:
                    #         #     trainer.push_to_hub()
                    #         trainer.push_to_hub()
                    #         # save model
                    #         # MODEL_DIR = os.getenv('MODEL_DIR', './data/checkpoint')
                    #         # FINETUNED_MODEL_NAME = os.getenv('FINETUNED_MODEL_NAME',hf_model_id)
                    #         # chk_path = str(pathlib.Path(MODEL_DIR) / FINETUNED_MODEL_NAME)
                    #         # print(f"Model is trained and saved as {chk_path}")
                    #         # trainer.save_model(chk_path)
                    #         # push to hub
                            
                    #         # free the memory again
                    #         del model
                    #         del trainer
                    #         torch.cuda.empty_cache()
                    CHANNEL_STATUS[channel_name]["status"] = "done"
                    output_dir = "./data/checkpoint"
                    print(push_to_hub)
                    if push_to_hub:
                        import datetime
                        output_dir = "./data/checkpoint"
                        now = datetime.datetime.now()
                        date_str = now.strftime("%Y%m%d")
                        time_str = now.strftime("%H%M%S")
                        version = f'{date_str}-{time_str}'

                        upload_checkpoint(project, version, output_dir)
                    # if push_to_hub:
                    #     import datetime
                    #     output_dir = "./data/checkpoint"
                    #     now = datetime.datetime.now()
                    #     date_str = now.strftime("%Y%m%d")
                    #     time_str = now.strftime("%H%M%S")
                    #     version = f'{date_str}-{time_str}'

                    #     for root, dirs, files in os.walk(output_dir):
                    #         for idx, file in enumerate(files):
                    #             file_path = os.path.join(root, file)
                    #             relative_path = os.path.relpath(file_path, output_dir)
                    #             folder_name = os.path.dirname(relative_path)
                    #             # path_upload = os.path.join(version, folder_name)
                                 
                    #             if idx == len(files) - 1:   
                    #                 upload_checkpoint(file_path, project_id, token, folder_name, version, True)
                    #             else:
                    #                 upload_checkpoint(file_path, project_id, token, folder_name, version)
                
                train_thread = threading.Thread(target=func_train_model, args=(clone_dir, project_id, token, checkpoint_version, checkpoint_id, dataset_version, dataset_id,model_id,world_size,rank,master_add,master_port,prompt, absolute_path, channel_log, hf_model_id, push_to_hub, push_to_hub_token,host_name))
                train_thread.start()
                 
                return {"message": "train completed successfully", "channel_name": channel_name}
            # except Exception as e:
            #     return {"message": f"train failed: {e}"}
        elif command.lower() == "stop":
            subprocess.run(["pkill", "-9", "-f", "./inference/generate.py"])
            return {"message": "train stop successfully", "result": "Done"}
        
        elif command.lower() == "tensorboard":
            def run_tensorboard():
                # train_dir = os.path.join(os.getcwd(), "{project_id}")
                # log_dir = os.path.join(os.getcwd(), "logs")
                p = subprocess.Popen(f"tensorboard --logdir /app/data/checkpoint/runs --host 0.0.0.0 --port=6006", stdout=subprocess.PIPE, stderr=None, shell=True)
                out = p.communicate()
                print(out)
            import threading
            tensorboard_thread = threading.Thread(target=run_tensorboard)
            tensorboard_thread.start()
            return {"message": "tensorboardx started successfully"}
        
        elif command.lower() == "predict":
            # from misc import get_device_count
            # try:
                import torch
                from transformers import pipeline
            # try:
                # checkpoint = kwargs.get("checkpoint")
                # imagebase64 = kwargs.get("image","")
                prompt = kwargs.get("prompt", None)
                model_id = kwargs.get("model_id", "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B")
                text = kwargs.get("text", None)
                token_length = kwargs.get("token_lenght", 30)
                task = kwargs.get("task", "")
                voice = kwargs.get("voice", "")
                max_new_token = kwargs.get("max_new_token", 256)
                temperature = kwargs.get("temperature", 0.7)
                top_k = kwargs.get("top_k", 50)
                top_p = kwargs.get("top_p", 0.95)

                predictions = []

                if not prompt or prompt == "":
                    prompt = text

                from huggingface_hub import login 
                hf_access_token = kwargs.get("hf_access_token", "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")
                login(token = hf_access_token)
                def smart_pipeline(model_id: str, token: str, local_dir="./data/checkpoint", task="text-generation"):
                    try:
                        import os
                        model_name = model_id.split("/")[-1]
                        local_model_dir = os.path.join(local_dir, model_name)

                        # Kiểm tra xem model đã có local chưa
                        if os.path.exists(local_model_dir) and os.path.exists(os.path.join(local_model_dir, "config.json")):
                            print(f"✅ Loading model from local: {local_model_dir}")
                            model_source = local_model_dir
                        else:
                            print(f"☁️ Loading model from HuggingFace Hub: {model_id}")
                            model_source = model_id
                    except:
                        print(f"☁️ Loading model from HuggingFace Hub: {model_id}")
                        model_source = model_id

                    # Xác định dtype và device
                    if torch.cuda.is_available():
                        if torch.cuda.is_bf16_supported():
                            dtype = torch.bfloat16
                        else:
                            dtype = torch.float16

                        print("Using CUDA.")
                        pipe = pipeline(
                            task,
                            model=model_source,
                            torch_dtype=dtype,
                            device_map="auto",
                            token=token,
                            max_new_tokens=256
                        )
                    else:
                        print("Using CPU.")
                        pipe = pipeline(
                            task,
                            model=model_source,
                            device_map="cpu",
                            token=token,
                            max_new_tokens=256
                        )

                    return pipe

                _model = smart_pipeline(model_id, hf_access_token)
                generated_text = qa_without_context(_model, prompt)
          
                print(generated_text)
                predictions.append({
                    'result': [{
                        'from_name': "generated_text",
                        'to_name': "text_output",
                        'type': 'textarea',
                        'value': {
                            'text': [generated_text]
                        }
                    }],
                    'model_version': ""
                })

                return {"message": "predict completed successfully", "result": predictions}
        elif command.lower() == "prompt_sample":
                task = kwargs.get("task", "")
                if task == "question-answering":
                    prompt_text = f"""
                   Here is the context: 
                    {{context}}

                    Based on the above context, provide an answer to the following question: 
                    {{question}}

                    Answer:
                    """
                elif task == "text-classification":
                   prompt_text = f"""
                    Summarize the following text into a single, concise paragraph focusing on the key ideas and important points:

                    Text: 
                    {{context}}

                    Summary:
                    """
                
                elif task == "summarization":
                    prompt_text = f"""
                    Summarize the following text into a single, concise paragraph focusing on the key ideas and important points:

                    Text: 
                    {{context}}

                    Summary:
                    """
                return {"message": "prompt_sample completed successfully", "result":prompt_text}

        elif command.lower() == "action-example":
            return {"message": "Done", "result": "Done"}
        
        elif command == "status":
            channel = kwargs.get("channel", None)
            
            if channel:
                # Nếu có truyền kênh cụ thể
                status_info = CHANNEL_STATUS.get(channel)
                if status_info is None:
                    return {"channel": channel, "status": "not_found"}
                elif isinstance(status_info, dict):
                    return {"channel": channel, **status_info}
                else:
                    return {"channel": channel, "status": status_info}
            else:
                # Lấy tất cả kênh
                if not CHANNEL_STATUS:
                    return {"message": "No channels available"}
                
                channels = []
                for ch, info in CHANNEL_STATUS.items():
                    if isinstance(info, dict):
                        channels.append({"channel": ch, **info})
                    else:
                        channels.append({"channel": ch, "status": info})
                
                return {"channels": channels}
        else:
            return {"message": "command not supported", "result": None}
            
            
            # return {"message": "train completed successfully"}
        
    # def model(self, project, **kwargs):
    #     import torch
    #     import gradio as gr
    #     from transformers import pipeline
    #     task = kwargs.get("task", "text-generation")
    #     model_id = kwargs.get("model_id", "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B")
    #     world_size = kwargs.get("world_size", 1)
    #     rank = kwargs.get("rank", 0)
    #     master_add = kwargs.get("master_add","127.0.0.1")
    #     master_port = kwargs.get("master_port", "23456")
    #     project_id = project

    #     print(f'''\
    #     Project ID: {project_id}
    #     Label config: {self.label_config}
    #     Parsed JSON Label config: {self.parsed_label_config}''')
    #     from huggingface_hub import login 
    #     hf_access_token = kwargs.get("hf_access_token", "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")
    #     login(token = hf_access_token)
       
    #     #========================== chatbot =======================
    #     import gradio as gr
    #     import torch
    #     from dataclasses import asdict, dataclass
    #     from textwrap import dedent
    #     from types import SimpleNamespace
    #     from loguru import logger
    #     # Log in to Hugging Face Hub
    #     from huggingface_hub.hf_api import HfFolder; HfFolder.save_token('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')

    #     # Determine the device to use (GPU if available, otherwise CPU)
    #     device = 0 if torch.cuda.is_available() else -1

    #     # Dictionary mapping model names to their Hugging Face Hub identifiers
    #     llama_models = {
    #         "DeepSeek-R1-Distill-Qwen-1.5B": "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
    #         "DeepSeek-R1-Distill-Qwen-7B": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
    #         "DeepSeek-R1-Distill-Llama-8B": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
    #         "DeepSeek-R1-Distill-Qwen-14B": "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
    #         "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B": "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
    #         "deepseek-ai/DeepSeek-R1-Distill-Llama-70B": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
    #         # "Llama3.2": "meta-llama/Llama-3.2-1B",
    #         # "Qwen2.5-7B-Instruct-1M": "Qwen/Qwen2.5-7B-Instruct-1M",
    #         # "Qwen2.5-14B-Instruct-1M": "Qwen/Qwen2.5-14B-Instruct-1M",
    #         # "llama-nemotron": "itsnebulalol/Llama-3.2-Nemotron-3B-Instruct",
    #     }
    #     SYSTEM_PROMPT = "You are a helpful assistant."
    #     MAX_MAX_NEW_TOKENS = 4096  # sequence length 2048
    #     MAX_NEW_TOKENS = 512
    #     @dataclass
    #     class Config:
    #         max_new_tokens: int = MAX_NEW_TOKENS
    #         repetition_penalty: float = 1.1
    #         temperature: float = 1.0
    #         top_k: int = 0
    #         top_p: float = 0.9


    #     # stats_default = SimpleNamespace(llm=model, system_prompt=SYSTEM_PROMPT, config=Config())
    #     stats_default = SimpleNamespace(llm=None, system_prompt=SYSTEM_PROMPT, config=Config())
    #     # Function to load the model and tokenizer
    #     def load_model(model_name):
    #         from transformers import AutoModelForCausalLM, AutoTokenizer
    #         print(model_name)
    #         model = AutoModelForCausalLM.from_pretrained(
    #             model_name,
    #             trust_remote_code=True,
    #             device_map="cuda",
    #             quantization_config=None
    #         )
    #         model.to('cuda')
    #         tokenizer = AutoTokenizer.from_pretrained(model_name)
    #         # tokenizer.pad_token = tokenizer.eos_token
    #         tokenizer.pad_token_id =  tokenizer.eos_token_id
    #         # tokenizer.padding_side = 'left'
    #         return model,tokenizer

    #     # Cache to store loaded models
    #     model_cache = {}
    #     tokenizer_cache= {}
    #     # Function to generate chat responses
    #     def generate_chat(user_input, history, model_choice):
            
    #         # Load the model if not already cached
    #         model,tokenizer = load_model(llama_models[model_choice])
    #         # try:
    #         #     model = model_cache[model_choice]
    #         #     tokenizer = tokenizer_cache[model_choice]
    #         # except KeyError:
    #         #     model,tokenizer = load_model(llama_models[model_choice])
    #         #     model_cache[model_choice] = model
    #         #     tokenizer_cache[model_choice] = tokenizer
        
    #         # Initial system prompt
    #         system_prompt = {"role": "system", "content": stats_default.system_prompt}

    #         # Initialize history if it's None
    #         if history is None:
    #             history = [system_prompt]
    #         # Append user input to history
    #         history.append({"role": "user", "content": user_input})
        
    #         text = tokenizer.apply_chat_template(
    #             [{"role": "system", "content": stats_default.system_prompt},{"role": "user", "content": user_input}],
    #             tokenize=False,
    #             add_generation_prompt=True
    #         )
    #         inputs = tokenizer([text], return_tensors="pt", padding=True, truncation=True)

    #         outputs = model.generate(
    #             input_ids=inputs["input_ids"].to(model.device),
    #             attention_mask=inputs["attention_mask"].to(model.device),
    #             max_length=stats_default.config.max_new_tokens, ##change this to align with the official usage
    #             num_return_sequences=2,
    #             do_sample=True,  ##change this to align with the official usage,
    #             top_p=stats_default.config.top_p, top_k=stats_default.config.top_k, temperature=stats_default.config.temperature
    #             , pad_token_id=tokenizer.eos_token_id
    #         )
    #         generated_ids = [
    #             output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs["input_ids"], outputs)
    #         ]

    #         outputs = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
    #         response=outputs[0]
    #         print(outputs)
    #         # Append model response to history
    #         history.append({"role": "assistant", "content": response})
            
    #         return history

    #     # Create Gradio interface
    #     css = """
    #         .importantButton {
    #             background: linear-gradient(45deg, #7e0570,#5d1c99, #6e00ff) !important;
    #             border: none !important;
    #         }
    #         .importantButton:hover {
    #             background: linear-gradient(45deg, #ff00e0,#8500ff, #6e00ff) !important;
    #             border: none !important;
    #         }
    #         .disclaimer {font-variant-caps: all-small-caps; font-size: xx-small;}
    #         .xsmall {font-size: x-small;}
    #     """
    #     with gr.Blocks(
    #                 theme=gr.themes.Soft(text_size="sm"),
    #                 title="Deepseek R1 Chatbot",
    #                 css=css,
    #             ) as demo:
    #         stats = gr.State(stats_default)
    #         """Do exmaple_list css."""
    #         # pylint: disable=invalid-name, line-too-long,


    #         etext = """In America, where cars are an important part of the national psyche, a decade ago people had suddenly started to drive less, which had not happened since the oil shocks of the 1970s. """
    #         example_list = [
    #             ["What are the top A.I. companies in the world?"],
    #             [
    #                 " What is deep learning?"
    #             ],
    #             ["What is natural language processing (NLP)?"],
    #             [
    #                 "Will robotics kill jobs or create them?"
    #             ],
    #             [
    #                 "A.I. in gaming and sports betting."
    #             ],
    #             ["What is artificial intelligence?"],
    #             ["What role will A.I. play in health care?"],
    #             [
    #                 "A.I. in self-driving cars?"
    #             ],
    #             [" A.I. in investment and finance."],
    #             [" A.I. in marketing and advertising."],
    #             [" A.. in inductry and buildings."],
    #             [" A.I. and the future of work."],
    #             ["Let talkk me about DeepSeek R1"],
    #             ["Let talkk me about Nemotron"],
    #             ["Let talkk me about Kimi k1.5"],
    #             ["Let talkk me about Qwen2.5 1M tokens"],
    #             ["What is the AI Control Problem?"],
    #             ["Where are we with the AI Control Problem currently?"],
    #             ["What Is AI Safety?"],
    #         ]
    #         # if task == "text-generation":
    #         #       with gr.Tab(label=task):
    #         #             # demo_text_generation.render()
    #         #             demo_chatbot.render()
    #         #     elif task == "summarization":
    #         #       with gr.Tab(label=task):
    #         #             # demo_summarization.render()
    #         #             demo_chatbot.render()
    #         #     elif task == "question-answering":
    #         #        with gr.Tab(label=task):
    #         #             # demo_question_answering.render()
    #         #             demo_chatbot.render()
    #         #     elif task == "text-classification":
    #         #         with gr.Tab(label=task):
    #         #                 # demo_text_classification.render()
    #         #                 demo_chatbot.render()
    #         #     elif task == "sentiment-analysis":
    #         #       with gr.Tab(label=task):
    #         #             # demo_sentiment_analysis.render()
    #         #             demo_chatbot.render()
    #         #     elif task == "ner":
    #         #        with gr.Tab(label=task):
    #         #             # demo_ner.render()
    #         #             demo_chatbot.render()
    #         #     elif task == "chatbot":
    #         #       with gr.Tab(label=task):
    #         #             demo_chatbot.render()
    #         #     elif task == "text2text-generation":
    #         #        with gr.Tab(label=task):
    #         #             # demo_text2text_generation.render()
    #         #             demo_chatbot_1b.render()
    #         gr.Markdown("<h1><center>Chat with DeepSeek R1 Models</center></h1>")
    #         with gr.Row():
    #             with gr.Column(scale=5):
    #                 # Dropdown to select model
    #                 model_choice = gr.Dropdown(list(llama_models.keys()), label="Select LLM Model", type="value")
    #                 # Chatbot interface
    #                 chatbot = gr.Chatbot(label="Chatbot Interface", type="messages")
    #                 # Textbox for user input
    #                 txt_input = gr.Textbox(show_label=False, placeholder="Type your message here...")

    #                 # Function to handle user input and generate response
    #                 def respond(user_input, chat_history,model_choice):
    #                     # model_choice= "DeepSeek-R1-1B"
    #                     if model_choice is None:
    #                         model_choice = list(llama_models.keys())[0]
    #                     updated_history = generate_chat(user_input, chat_history, model_choice)
    #                     return "", updated_history

    #                 # Submit user input on pressing Enter
    #                 txt_input.submit(respond, [txt_input, chatbot,model_choice], [txt_input, chatbot])
    #                 # Button to submit user input
    #                 submit_btn = gr.Button("Submit")
    #                 submit_btn.click(respond, [txt_input, chatbot,model_choice], [txt_input, chatbot])
    #         with gr.Row():
    #             with gr.Accordion(label="Advanced Options", open=False):
    #                 system_prompt = gr.Textbox(
    #                     label="System prompt",
    #                     value=stats_default.system_prompt,
    #                     lines=3,
    #                     visible=True,
    #                 )
    #                 max_new_tokens = gr.Slider(
    #                     label="Max new tokens",
    #                     minimum=1,
    #                     maximum=MAX_MAX_NEW_TOKENS,
    #                     step=1,
    #                     value=stats_default.config.max_new_tokens,
    #                 )
    #                 repetition_penalty = gr.Slider(
    #                     label="Repetition penalty",
    #                     minimum=0.1,
    #                     maximum=40.0,
    #                     step=0.1,
    #                     value=stats_default.config.repetition_penalty,
    #                 )
    #                 temperature = gr.Slider(
    #                     label="Temperature",
    #                     minimum=0.51,
    #                     maximum=40.0,
    #                     step=0.1,
    #                     value=stats_default.config.temperature,
    #                 )
    #                 top_p = gr.Slider(
    #                     label="Top-p (nucleus sampling)",
    #                     minimum=0.05,
    #                     maximum=1.0,
    #                     step=0.05,
    #                     value=stats_default.config.top_p,
    #                 )
    #                 top_k = gr.Slider(
    #                     label="Top-k",
    #                     minimum=0,
    #                     maximum=1000,
    #                     step=1,
    #                     value=stats_default.config.top_k,
    #                 )

    #                 def system_prompt_fn(system_prompt):
    #                     stats.value.system_prompt = system_prompt
    #                     logger.debug(f"{stats.value.system_prompt=}")

    #                 def max_new_tokens_fn(max_new_tokens):
    #                     stats.value.config.max_new_tokens = max_new_tokens
    #                     logger.debug(f"{stats.value.config.max_new_tokens=}")

    #                 def repetition_penalty_fn(repetition_penalty):
    #                     stats.value.config.repetition_penalty = repetition_penalty
    #                     logger.debug(f"{stats.value=}")

    #                 def temperature_fn(temperature):
    #                     stats.value.config.temperature = temperature
    #                     logger.debug(f"{stats.value=}")

    #                 def top_p_fn(top_p):
    #                     stats.value.config.top_p = top_p
    #                     logger.debug(f"{stats.value=}")

    #                 def top_k_fn(top_k):
    #                     stats.value.config.top_k = top_k
    #                     logger.debug(f"{stats.value=}")

    #                 system_prompt.change(system_prompt_fn, system_prompt)
    #                 max_new_tokens.change(max_new_tokens_fn, max_new_tokens)
    #                 repetition_penalty.change(repetition_penalty_fn, repetition_penalty)
    #                 temperature.change(temperature_fn, temperature)
    #                 top_p.change(top_p_fn, top_p)
    #                 top_k.change(top_k_fn, top_k)

    #                 def reset_fn(stats_):
    #                     logger.debug("reset_fn")
    #                     stats_ = gr.State(stats_default)
    #                     logger.debug(f"{stats_.value=}")
    #                     chatbot.reset()
    #                     return (
    #                         stats_,
    #                         stats_default.system_prompt,
    #                         stats_default.config.max_new_tokens,
    #                         stats_default.config.repetition_penalty,
    #                         stats_default.config.temperature,
    #                         stats_default.config.top_p,
    #                         stats_default.config.top_k,
    #                     )

    #                 reset_btn = gr.Button("Reset")
    #                 reset_btn.click(
    #                     reset_fn,
    #                     stats,
    #                     [
    #                         stats,
    #                         system_prompt,
    #                         max_new_tokens,
    #                         repetition_penalty,
    #                         temperature,
    #                         top_p,
    #                         top_k,
    #                     ],
    #                 )
    #         with gr.Row():
    #             with gr.Accordion("Example inputs", open=True):
    #                 etext = """In America, where cars are an important part of the national psyche, a decade ago people had suddenly started to drive less, which had not happened since the oil shocks of the 1970s. """
    #                 examples = gr.Examples(
    #                     examples=example_list,
    #                     inputs=[txt_input],
    #                     examples_per_page=60,
    #                 )
            

    #     # Launch the Gradio demo

    #     gradio_app, local_url, share_url = demo.launch(share=True, quiet=True, prevent_thread_lock=True, server_name='0.0.0.0',show_error=False,show_api=False)
   
    #     return {"share_url": share_url, 'local_url': local_url}
    @mcp.tool()
    def model(self, **kwargs):
        
        import gradio as gr
        from transformers import pipeline
        # task = kwargs.get("task", "text-generation")
        task = kwargs.get("task", "chat")
        model_id = kwargs.get("model_id", "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B")
        if "deepseek" not in "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B":
             model_id =  "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
        project_id = kwargs.get("project_id", 0)

        print(f'''\
        Project ID: {project_id}
''')
        from huggingface_hub import login 
        hf_access_token = kwargs.get("hf_access_token", "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")
        login(token = hf_access_token)
        def load_model(task,model_id, project_id, temperature=None, top_p=None, top_k=None, max_new_token=None):
            from huggingface_hub import login 
            hf_access_token = kwargs.get("hf_access_token", "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")
            login(token = hf_access_token)
            if torch.cuda.is_available():
                if torch.cuda.is_bf16_supported():
                    dtype = torch.bfloat16
                else:
                    dtype = torch.float16

                print("CUDA is available.")
                
                if not temperature:
                    _model = pipeline(
                    task,
                    model=model_id, 
                    torch_dtype=dtype, 
                    device_map="auto",  # Hoặc có thể thử "cpu" nếu không ổn,
                    # max_new_tokens=256,
                    token = "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"
                    )
                else:
                    _model = pipeline(
                        task,
                        model=model_id, 
                        torch_dtype=dtype, 
                        device_map="auto",  # Hoặc có thể thử "cpu" nếu không ổn,
                        # max_new_tokens=256,
                        token = "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",
                        max_new_tokens=int(max_new_token),
                        temperature=float(temperature),
                        top_k=float(top_k),
                        top_p=float(top_p)
                    )
            else:
                print("No GPU available, using CPU.")
                if not temperature:
                    _model = pipeline(
                    task,
                    model=model_id, 
                    torch_dtype=dtype, 
                    device_map="auto",  # Hoặc có thể thử "cpu" nếu không ổn,
                    # max_new_tokens=256,
                    token = "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"
                    )
                else:
                    _model = pipeline(
                        task,
                        model=model_id, 
                        device_map="cpu",
                        # max_new_tokens=256,
                        token = "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",
                        max_new_tokens=int(max_new_token),
                        temperature=float(temperature),
                        top_k=float(top_k),
                        top_p=float(top_p),
                    )
            # try:
            #     channel_deploy = f'project/{project_id}/deploy-history'
            #     client, sub = setup_client(channel_deploy)
            #     send_message(sub,{"refresh": True})
            #     client.disconnect()  # Đóng kết nối client
            # except Exception as e:
            #     print(e)

            return _model
        
        # load_model(task,model_id,project_id)
        
        def generate_response(input_text, temperature, top_p, top_k, max_new_token):
            load_model("text-generation", model_id, project_id, temperature, top_p, top_k, max_new_token)
            # _model = load_model(model_id)
            # prompt_text = f"""
            #        Here is the context: 
            #         {{context}}

            #         Based on the above context, provide an answer to the following question using only a single word or phrase from the context without repeating the question or adding any extra explanation: 
            #         {{question}}

            #         Answer:
            #         """
            # prompt = prompt_text
           
             
            # if not prompt_text or prompt_text == "":
            #     prompt = input_text
            messages = [
                {"role": "system", "content":  "You are a helpful assistant."},
                {"role": "user", "content": input_text},
            ]
            # outputs = _model(
            #     messages,
            #     max_new_tokens=256,
            # )
            result = _model(messages, max_length=1024)
           
            generated_text = result[0]['generated_text']
             
            # if input_text and prompt_text:
            #     generated_text = qa_with_context(_model, input_text, prompt_text)
            # elif input_text and not prompt_text:
            #     generated_text = qa_without_context(_model, prompt_text)
            # else:
            #     generated_text = qa_with_context(_model, prompt_text)

            return generated_text
        
        def summarization_response(input_text, temperature, top_p, top_k, max_new_token):
            load_model("text-generation", model_id, project_id, temperature, top_p, top_k, max_new_token)
            # _model = load_model(model_id)
            generated_text = text_summarization(_model, input_text)
  
            return generated_text
        
        def text_classification_response(input_text,categories_text, temperature, top_p, top_k, max_new_token):
            load_model("text-generation", model_id, project_id, temperature, top_p, top_k, max_new_token)  
            # prompt_text = f"""
            #         Summarize the following text into a single, concise paragraph focusing on the key ideas and important points:

            #         Text: 
            #         {{context}}

            #         Summary:
            #         """
                
            # _model = load_model(model_id)
            generated_text = text_classification(_model, input_text, categories_text)
            return generated_text
        
        def question_answering_response(context_textbox,question_textbox, temperature, top_p, top_k, max_new_token):
            load_model("text-generation", model_id, project_id, temperature, top_p, top_k, max_new_token)
            # _model = load_model(model_id)
            if input_text and question_textbox:
                generated_text = qa_with_context(_model, context_textbox, question_textbox)
            elif context_textbox and not question_textbox:
                generated_text = qa_without_context(_model, question_textbox)
            else:
                generated_text = qa_with_context(_model, question_textbox)

            return generated_text
        
        def chatbot_continuous_chat(history, user_input, temperature, top_p, top_k, max_new_token):
            load_model("text-generation", model_id, project_id, temperature, top_p, top_k, max_new_token)
            generated_text = chatbot_with_history(_model, history, user_input)
            return generated_text
        
        with gr.Blocks() as demo_text_generation:
            with gr.Row():
                with gr.Column():
                    with gr.Group():
                        input_text = gr.Textbox(label="Input text")
                        # prompt_text = gr.Textbox(label="Prompt text")
                        temperature = gr.Slider(
                            label="Temperature",
                            minimum=0.0,
                            maximum=100.0,
                            step=0.1,
                            value=0.9
                        )
                        top_p = gr.Slider(
                            label="Top_p",
                            minimum=0.0,
                            maximum=1.0,
                            step=0.1,
                            value=0.6
                        )
                        top_k = gr.Slider(
                            label="Top_k",
                            minimum=0,
                            maximum=100,
                            step=1,
                            value=0
                        )
                        max_new_token = gr.Slider(
                            label="Max new tokens",
                            minimum=1,
                            maximum=1024,
                            step=1,
                            value=256
                        )
                    btn = gr.Button("Submit")
                with gr.Column():
                    output_text = gr.Textbox(label="Output text")
            # gr.on(
            #     triggers=[input_text.submit, temperature.submit, top_p.submit, top_k.submit, max_new_token.submit, btn.click],
            #     fn=generate_response,
            #     inputs=[input_text, temperature, top_p, top_k, max_new_token],
            #     outputs=output_text,
            #     api_name=task,
            # )
            btn.click(
                fn=generate_response,
                inputs=[input_text, temperature, top_p, top_k, max_new_token],
                outputs=output_text
            )
        
        with gr.Blocks() as demo_summarization:
            with gr.Row():
                with gr.Column():
                    with gr.Group():
                        input_text = gr.Textbox(label="Input text")
                        temperature = gr.Slider(
                            label="Temperature",
                            minimum=0.0,
                            maximum=100.0,
                            step=0.1,
                            value=0.9
                        )
                        top_p = gr.Slider(
                            label="Top_p",
                            minimum=0.0,
                            maximum=1.0,
                            step=0.1,
                            value=0.6
                        )
                        top_k = gr.Slider(
                            label="Top_k",
                            minimum=0,
                            maximum=100,
                            step=1,
                            value=0
                        )
                        max_new_token = gr.Slider(
                            label="Max new tokens",
                            minimum=1,
                            maximum=1024,
                            step=1,
                            value=256
                        )
                        # prompt_text = gr.Textbox(label="Prompt text")
                    btn = gr.Button("Submit")
                with gr.Column():
                    output_text = gr.Textbox(label="Output text")
            # gr.on(
            #     triggers=[input_text.submit, temperature.submit, top_p.submit, top_k.submit, max_new_token.submit, btn.click],
            #     fn=summarization_response,
            #     inputs=[input_text, temperature, top_p, top_k, max_new_token],
            #     outputs=output_text,
            #     api_name=task,
            # )
            btn.click(
                fn=summarization_response,
                inputs=[input_text, temperature, top_p, top_k, max_new_token],
                outputs=output_text
            )
        
        with gr.Blocks() as demo_question_answering:
            with gr.Row():
                with gr.Column():
                    with gr.Group():
                        context_textbox = gr.Textbox(label="Context text")
                        question_textbox = gr.Textbox(label="Question text")
                        temperature = gr.Slider(
                            label="Temperature",
                            minimum=0.0,
                            maximum=100.0,
                            step=0.1,
                            value=0.9
                        )
                        top_p = gr.Slider(
                            label="Top_p",
                            minimum=0.0,
                            maximum=1.0,
                            step=0.1,
                            value=0.6
                        )
                        top_k = gr.Slider(
                            label="Top_k",
                            minimum=0,
                            maximum=100,
                            step=1,
                            value=0
                        )
                        max_new_token = gr.Slider(
                            label="Max new tokens",
                            minimum=1,
                            maximum=1024,
                            step=1,
                            value=256
                        )
                       
                    btn = gr.Button("Submit")
                with gr.Column():
                    output_text =   gr.Textbox(label="Response:")
            

            # gr.Examples(
            #    inputs=[input_text],
            #     outputs=output_text,
            #     fn=question_answering_response,
            #     api_name=False,
            # )

            # gr.on(
            #     triggers=[context_textbox.submit,question_textbox.submit, temperature.submit, top_p.submit, top_k.submit, max_new_token.submit, btn.click],
            #     fn=question_answering_response,
            #     inputs=[context_textbox, question_textbox, temperature, top_p, top_k, max_new_token],
            #     outputs=output_text,
            #     api_name=task,
            # )
            btn.click(
                fn=question_answering_response,
                inputs=[context_textbox, question_textbox, temperature, top_p, top_k, max_new_token],
                outputs=output_text
            )
        
        with gr.Blocks() as demo_text_classification:
            with gr.Row():
                with gr.Column():
                    with gr.Group():
                        input_text = gr.Textbox(label="Input text")
                        categories_text = gr.Textbox(label="Categories text")
                        temperature = gr.Slider(
                            label="Temperature",
                            minimum=0.0,
                            maximum=100.0,
                            step=0.1,
                            value=0.9
                        )
                        top_p = gr.Slider(
                            label="Top_p",
                            minimum=0.0,
                            maximum=1.0,
                            step=0.1,
                            value=0.6
                        )
                        top_k = gr.Slider(
                            label="Top_k",
                            minimum=0,
                            maximum=100,
                            step=1,
                            value=0
                        )
                        max_new_token = gr.Slider(
                            label="Max new tokens",
                            minimum=1,
                            maximum=1024,
                            step=1,
                            value=256
                        )
                # with gr.Column():
                #     with gr.Group():
                #         input_text = gr.Textbox(label="Input text")
                    btn = gr.Button("Submit")
                with gr.Column():
                    output_text = gr.Textbox(label="Response:")

            
            # gr.on(
            #     triggers=[input_text.submit,categories_text.submit, temperature.submit, top_p.submit, top_k.submit, max_new_token.submit, btn.click],
            #     fn=text_classification_response,
            #     inputs=[input_text, categories_text, temperature, top_p, top_k, max_new_token],
            #     outputs=output_text,
            #     api_name=task,
            # )
            btn.click(
                fn=text_classification_response,
                inputs=[input_text, categories_text, temperature, top_p, top_k, max_new_token],
                outputs=output_text
            )
        
        def sentiment_classifier(text, temperature, top_p, top_k, max_new_token):
            try:
                sentiment_classifier = pipeline("sentiment-analysis", temperature=temperature, top_p=top_p, top_k=top_k, max_new_token=max_new_token)
                sentiment_response = sentiment_classifier(text)
                # label = sentiment_response[0]['label']
                # score = sentiment_response[0]['score']
                print(sentiment_response)
                import json
                return json.dumps(sentiment_response)
            except Exception as e:
                return str(e)
        
        with gr.Blocks() as demo_sentiment_analysis:
            with gr.Row():
                with gr.Column():
                    with gr.Group():
                        input_text = gr.Textbox(label="Input text")
                        temperature = gr.Slider(
                            label="Temperature",
                            minimum=0.0,
                            maximum=100.0,
                            step=0.1,
                            value=0.9
                        )
                        top_p = gr.Slider(
                            label="Top_p",
                            minimum=0.0,
                            maximum=1.0,
                            step=0.1,
                            value=0.6
                        )
                        top_k = gr.Slider(
                            label="Top_k",
                            minimum=0,
                            maximum=100,
                            step=1,
                            value=0
                        )
                        max_new_token = gr.Slider(
                            label="Max new tokens",
                            minimum=1,
                            maximum=1024,
                            step=1,
                            value=256
                        )
                    btn = gr.Button("Submit")
                with gr.Column():
                    
                    output_text = gr.Textbox(label="Output text")
                    # score_text = gr.Label(label="Score: ")

            # gr.on(
            #     triggers=[input_text.submit, temperature.submit, top_p.submit, top_k.submit, max_new_token.submit, btn.click],
            #     fn=sentiment_classifier,
            #     inputs=[input_text, temperature, top_p, top_k, max_new_token],
            #     outputs=[label_text, score_text],
            #     api_name=task,
            # )
            btn.click(
                fn=sentiment_classifier,
                inputs=[input_text, temperature, top_p, top_k, max_new_token],
                outputs=output_text
            )

        def predict_entities(input_text, categories_text, temperature, top_p, top_k, max_new_token):
            #  # Initialize the text-generation pipeline with your model
            # pipe = pipeline(task, model=model_id)
            # # Use the loaded model to identify entities in the text
            # entities = pipe(text)
            # # Highlight identified entities in the input text
            # highlighted_text = text
            # for entity in entities:
            #     entity_text = text[entity['start']:entity['end']]
            #     replacement = f"<span style='border: 2px solid green;'>{entity_text}</span>"
            #     highlighted_text = highlighted_text.replace(entity_text, replacement)
            # return highlighted_text
            load_model("text-generation", model_id, project_id, temperature, top_p, top_k, max_new_token)
            generated_text = text_ner(_model, input_text, categories_text)
            return generated_text
        
        with gr.Blocks() as demo_ner:
            with gr.Row():
                with gr.Column():
                    with gr.Group():
                        input_text = gr.Textbox(label="Input text")
                        categories_text = gr.Textbox(label="Categories text")
                        temperature = gr.Slider(
                            label="Temperature",
                            minimum=0.0,
                            maximum=100.0,
                            step=0.1,
                            value=0.9
                        )
                        top_p = gr.Slider(
                            label="Top_p",
                            minimum=0.0,
                            maximum=1.0,
                            step=0.1,
                            value=0.6
                        )
                        top_k = gr.Slider(
                            label="Top_k",
                            minimum=0,
                            maximum=100,
                            step=1,
                            value=0
                        )
                        max_new_token = gr.Slider(
                            label="Max new tokens",
                            minimum=1,
                            maximum=1024,
                            step=1,
                            value=256
                        )
                    # with gr.Group():
                    #     input_text = gr.Textbox(label="Input text")
                    btn = gr.Button("Submit")
                with gr.Column():
                    output_text = gr.Textbox(label="Response:")

            # gr.Examples(
            #     inputs=[input_text],
            #     outputs=output_text,
            #     fn=generate_response,
            #     api_name=False,
            # )

            # gr.on(
            #     triggers=[input_text.submit,categories_text.submit, temperature.submit, top_p.submit, top_k.submit, max_new_token.submit, btn.click],
            #     fn=predict_entities,
            #     inputs=[input_text, categories_text, temperature, top_p, top_k, max_new_token],
            #     outputs=output_text,
            #     api_name=task,
            # )
            btn.click(
                fn=predict_entities,
                inputs=[input_text, categories_text, temperature, top_p, top_k, max_new_token],
                outputs=output_text
            )
        
        with gr.Blocks() as demo_text2text_generation:
            with gr.Row():
                with gr.Column():
                    with gr.Group():
                        input_text = gr.Textbox(label="Input text", placeholder="Enter your text here")
                        temperature = gr.Slider(
                            label="Temperature",
                            minimum=0.0,
                            maximum=100.0,
                            step=0.1,
                            value=1
                        )
                        top_p = gr.Slider(
                            label="Top_p",
                            minimum=0.0,
                            maximum=1.0,
                            step=0.1,
                            value=0.9
                        )
                        top_k = gr.Slider(
                            label="Top_k",
                            minimum=0,
                            maximum=100,
                            step=1,
                            value=0
                        )
                        max_new_token = gr.Slider(
                            label="Max new tokens",
                            minimum=1,
                            maximum=1024,
                            step=1,
                            value=256
                        )
                    btn = gr.Button("Submit")
                with gr.Column():
                    output_text = gr.Textbox(label="Output text")
            
            # Gắn sự kiện với nút Submit
            btn.click(
                fn=generate_response,
                inputs=[input_text, temperature, top_p, top_k, max_new_token],
                outputs=output_text
            )
            
        with gr.Blocks() as demo_chatbot:
            chatbot = gr.Chatbot(type="messages")
            with gr.Row():
                user_input = gr.Textbox(label="Your message", placeholder="Type your message here...")
            with gr.Row():
                temperature = gr.Slider(
                            label="Temperature",
                            minimum=0.0,
                            maximum=100.0,
                            step=0.1,
                            value=0.9
                        )
                top_p = gr.Slider(
                    label="Top_p",
                    minimum=0.0,
                    maximum=1.0,
                    step=0.1,
                    value=0.6
                )
                top_k = gr.Slider(
                    label="Top_k",
                    minimum=0,
                    maximum=100,
                    step=1,
                    value=0
                )
                max_new_token = gr.Slider(
                    label="Max new tokens",
                    minimum=1,
                    maximum=10000,
                    step=1,
                    value=1024
                )
            with gr.Row():
                btn = gr.Button("Send")

            # Bind function to button click
            btn.click(
                fn=chatbot_continuous_chat,
                inputs=[chatbot, user_input, temperature, top_p, top_k, max_new_token],  # Thêm các tham số vào hàm
                outputs=[chatbot, user_input]  # Cập nhật lại chatbot với phản hồi mới và xóa trường nhập liệu
            )


        DESCRIPTION = """\
        # LLM UI
        This is a demo of LLM UI.
        """
        with gr.Blocks(css="style.css") as demo:
            gr.Markdown(DESCRIPTION)

            with gr.Tabs():
                if task == "text-generation":
                    with gr.Tab(label=task):
                        demo_text_generation.render()
                elif task == "summarization":
                    with gr.Tab(label=task):
                        demo_summarization.render()
                elif task == "question-answering":
                    with gr.Tab(label=task):
                        demo_question_answering.render()
                elif task == "text-classification":
                    with gr.Tab(label=task):
                            demo_text_classification.render()
                elif task == "sentiment-analysis":
                    with gr.Tab(label=task):
                        demo_sentiment_analysis.render()
                elif task == "ner":
                    with gr.Tab(label=task):
                        demo_ner.render()
                # elif task == "fill-mask":
                #   with gr.Tab(label=task):
                #         demo_fill_mask.render()
                elif task == "text2text-generation":
                    with gr.Tab(label=task):
                        demo_text2text_generation.render()
                elif task == "chat":
                    with gr.Tab(label=task):
                        demo_chatbot.render()
                else:
                    return {"share_url": "", 'local_url': ""}
                    
        gradio_app, local_url, share_url = demo.launch(share=True, quiet=True, prevent_thread_lock=True, server_name='0.0.0.0',show_error=True)
   
        return {"share_url": share_url, 'local_url': local_url}

    @mcp.tool()
    def model_trial(self, project, **kwargs):
        import gradio as gr 

        return {"message": "Done", "result": "Done"}


        css = """
        .feedback .tab-nav {
            justify-content: center;
        }

        .feedback button.selected{
            background-color:rgb(115,0,254); !important;
            color: #ffff !important;
        }

        .feedback button{
            font-size: 16px !important;
            color: black !important;
            border-radius: 12px !important;
            display: block !important;
            margin-right: 17px !important;
            border: 1px solid var(--border-color-primary);
        }

        .feedback div {
            border: none !important;
            justify-content: center;
            margin-bottom: 5px;
        }

        .feedback .panel{
            background: none !important;
        }


        .feedback .unpadded_box{
            border-style: groove !important;
            width: 500px;
            height: 345px;
            margin: auto;
        }

        .feedback .secondary{
            background: rgb(225,0,170);
            color: #ffff !important;
        }

        .feedback .primary{
            background: rgb(115,0,254);
            color: #ffff !important;
        }

        .upload_image button{
            border: 1px var(--border-color-primary) !important;
        }
        .upload_image {
            align-items: center !important;
            justify-content: center !important;
            border-style: dashed !important;
            width: 500px;
            height: 345px;
            padding: 10px 10px 10px 10px
        }
        .upload_image .wrap{
            align-items: center !important;
            justify-content: center !important;
            border-style: dashed !important;
            width: 500px;
            height: 345px;
            padding: 10px 10px 10px 10px
        }

        .webcam_style .wrap{
            border: none !important;
            align-items: center !important;
            justify-content: center !important;
            height: 345px;
        }

        .webcam_style .feedback button{
            border: none !important;
            height: 345px;
        }

        .webcam_style .unpadded_box {
            all: unset !important;
        }

        .btn-custom {
            background: rgb(0,0,0) !important;
            color: #ffff !important;
            width: 200px;
        }

        .title1 {
            margin-right: 90px !important;
        }

        .title1 block{
            margin-right: 90px !important;
        }

        """

        with gr.Blocks(css=css) as demo:
            with gr.Row():
                with gr.Column(scale=10):
                    gr.Markdown(
                        """
                        # Theme preview: `AIxBlock`
                        """
                    )

            import numpy as np
            def predict(input_img):
                import cv2
                result = self.action(project, "predict",collection="",data={"img":input_img})
                print(result)
                if result['result']:
                    boxes = result['result']['boxes']
                    names = result['result']['names']
                    labels = result['result']['labels']
                    
                    for box, label in zip(boxes, labels):
                        box = [int(i) for i in box]
                        label = int(label)
                        input_img = cv2.rectangle(input_img, box, color=(255, 0, 0), thickness=2)
                        # input_img = cv2.(input_img, names[label], (box[0], box[1]), color=(255, 0, 0), size=1)
                        input_img = cv2.putText(input_img, names[label], (box[0], box[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        
                return input_img
            
            def download_btn(evt: gr.SelectData):
                print(f"Downloading {dataset_choosen}")
                return f'<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"><a href="/my_ml_backend/datasets/{evt.value}" style="font-size:50px"> <i class="fa fa-download"></i> Download this dataset</a>'
                
            def trial_training(dataset_choosen):
                print(f"Training with {dataset_choosen}")
                result = self.action(project, "train",collection="",data=dataset_choosen)
                return result['message']

            def get_checkpoint_list(project):
                print("GETTING CHECKPOINT LIST")
                print(f"Proejct: {project}")
                import os
                checkpoint_list = [i for i in os.listdir("my_ml_backend/models") if i.endswith(".pt")]
                checkpoint_list = [f"<a href='./my_ml_backend/checkpoints/{i}' download>{i}</a>" for i in checkpoint_list]
                if os.path.exists(f"my_ml_backend/{project}"):
                    for folder in os.listdir(f"my_ml_backend/{project}"):
                        if "train" in folder:
                            project_checkpoint_list = [i for i in os.listdir(f"my_ml_backend/{project}/{folder}/weights") if i.endswith(".pt")]
                            project_checkpoint_list = [f"<a href='./my_ml_backend/{project}/{folder}/weights/{i}' download>{folder}-{i}</a>" for i in project_checkpoint_list]
                            checkpoint_list.extend(project_checkpoint_list)
                
                return "<br>".join(checkpoint_list)

            def tab_changed(tab):
                if tab == "Download":
                    get_checkpoint_list(project=project)
            
            def upload_file(file):
                return "File uploaded!"
            
            with gr.Tabs(elem_classes=["feedback"]) as parent_tabs:
                with gr.TabItem("Image", id=0):   
                    with gr.Row():
                        gr.Markdown("## Input", elem_classes=["title1"])
                        gr.Markdown("## Output", elem_classes=["title1"])
                    
                    gr.Interface(predict, gr.Image(elem_classes=["upload_image"], sources="upload", container = False, height = 345,show_label = False), 
                                gr.Image(elem_classes=["upload_image"],container = False, height = 345,show_label = False), allow_flagging = False             
                    )


                # with gr.TabItem("Webcam", id=1):    
                #     gr.Image(elem_classes=["webcam_style"], sources="webcam", container = False, show_label = False, height = 450)

                # with gr.TabItem("Video", id=2):    
                #     gr.Image(elem_classes=["upload_image"], sources="clipboard", height = 345,container = False, show_label = False)

                # with gr.TabItem("About", id=3):  
                #     gr.Label("About Page")

                with gr.TabItem("Trial Train", id=2):
                    gr.Markdown("# Trial Train")
                    with gr.Column():
                        with gr.Column():
                            gr.Markdown("## Dataset template to prepare your own and initiate training")
                            with gr.Row():
                                #get all filename in datasets folder
                                if not os.path.exists(f"./datasets"):
                                    os.makedirs(f"./datasets")
                                datasets = [(f"dataset{i}", name) for i, name in enumerate(os.listdir('./datasets'))]
                                
                                dataset_choosen = gr.Dropdown(datasets, label="Choose dataset", show_label=False, interactive=True, type="value")
                                # gr.Button("Download this dataset", variant="primary").click(download_btn, dataset_choosen, gr.HTML())
                                download_link = gr.HTML("""
                                        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
                                        <a href='' style="font-size:24px"><i class="fa fa-download" ></i> Download this dataset</a>""")
                                
                                dataset_choosen.select(download_btn, None, download_link)
                                
                                #when the button is clicked, download the dataset from dropdown
                                # download_btn
                            gr.Markdown("## Upload your sample dataset to have a trial training")
                            # gr.File(file_types=['tar','zip'])
                            gr.Interface(predict, gr.File(elem_classes=["upload_image"],file_types=['tar','zip']), 
                                gr.Label(elem_classes=["upload_image"],container = False), allow_flagging = False             
                    )
                            with gr.Row():
                                gr.Markdown(f"## You can attemp up to {2} FLOps")
                                gr.Button("Trial Train", variant="primary").click(trial_training, dataset_choosen, None)
                
                # with gr.TabItem("Download"):
                #     with gr.Column():
                #         gr.Markdown("## Download")
                #         with gr.Column():
                #             gr.HTML(get_checkpoint_list(project))

        gradio_app, local_url, share_url = demo.launch(share=True, quiet=True, prevent_thread_lock=True, server_name='0.0.0.0',show_error=True)
   
        return {"share_url": share_url, 'local_url': local_url}

    @mcp.tool()
    def download(self, project, **kwargs):
        from flask import send_from_directory,request
        file_path = request.args.get('path')
        print(request.args)
        return send_from_directory(os.getcwd(), file_path)
    # def download(self, project, **kwargs):
    #     from flask import send_file
    #     file_path = kwargs.get("path","")
    #     if os.path.exists(os.path.join("/app/", file_path)):
    #         return send_file(os.path.join("/app/", file_path), as_attachment=True)
    #     else:
    #         print("file dont exist")
    #         return {"msg": "file dont exist"}
