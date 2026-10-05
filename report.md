# Vision OCR benchmark

Overall = mean of OCRBench accuracy and OmniAI JSON field accuracy. Cost is OpenRouter's billed `usage.cost`.

| Model | OCRBench % | JSON % | Overall % | $ / 1k images | Total $ | p50 s | Errors | Provider |
|---|---|---|---|---|---|---|---|---|
| google/gemini-3.1-flash-lite | 92.0 | 94.1 | 93.1 | $0.857 | $0.171 | 3.0 | 0/200 | Google |
| google/gemini-3.5-flash-lite | 90.0 | 92.0 | 91.0 | $0.872 | $0.174 | 1.9 | 0/200 | Google |
| qwen/qwen3.8-flash | 89.3 | 92.0 | 90.7 | $0.472 | $0.094 | 3.7 | 0/200 | Alibaba |
| inclusionai/ling-3.0-flash-vl | 92.0 | 89.0 | 90.5 | $0.107 | $0.021 | 4.4 | 0/200 | DeepInfra,Novita |
| z-ai/glm-5.3-flash | 88.7 | 91.9 | 90.3 | $0.546 | $0.109 | 2.6 | 0/200 | CoreWeave,Crusoe,Decart,Fireworks,Friendli,GMICloud,InferenceNet,Io Net,Modal,Parasail,Reka,StreamLake,Together,Wafer |
| moonshotai/kimi-k2.5 | 83.3 | 92.3 | 87.8 | $5.101 | $1.020 | 7.7 | 0/200 | Amazon Bedrock,AtlasCloud,Novita,Venice |
| qwen/qwen3.6-35b-a3b | 90.7 | 82.6 | 86.6 | $1.013 | $0.203 | 5.8 | 0/200 | AkashML,AtlasCloud,CoreWeave,Darkbloom,DeepInfra,Parasail,Phala,Reka,SiliconFlow,Venice |
| qwen/qwen3.5-9b | 89.3 | 81.7 | 85.5 | $0.392 | $0.078 | 10.2 | 0/200 | Darkbloom,DeepInfra,Parasail,SiliconFlow,Together,Venice |
| xiaomi/mimo-v2.6-flash | 79.3 | 88.7 | 84.0 | $0.405 | $0.081 | 13.7 | 0/200 | DeepInfra,Relace,Xiaomi |
| deepseek/deepseek-v4.1-flash | 80.0 | 86.8 | 83.4 | $1.464 | $0.293 | 3.5 | 0/200 | AtlasCloud,BaseTen,CoreWeave,DeepSeek,DekaLLM,GMICloud,InferenceNet,Makora,Morph,NextBit,Novita,Parasail,Relace,Together,Wafer |
| openai/gpt-6-luna | 66.0 | 92.3 | 79.1 | $0.373 | $0.075 | 3.1 | 0/200 | Azure,OpenAI |
| nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free | 85.3 | 67.4 | 76.4 | $0.000 | $0.000 | 11.4 | 0/200 | Nvidia |
| mistralai/mistral-small-3.2-24b-instruct | 66.7 | 81.5 | 74.1 | $0.249 | $0.050 | 3.0 | 0/200 | DeepInfra,Parasail,Venice |
| openai/gpt-5-nano | 64.7 | 42.6 | 53.7 | $0.275 | $0.055 | 4.7 | 0/200 | OpenAI |

## By category (%)

| Model | Key Information Extraction | Scene Text-centric VQA | Doc-oriented VQA | Non-Semantic Text Recognition | Digit String Recognition | Regular Text Recognition | Irregular Text Recognition | Artistic Text Recognition | Handwriting Recognition | JSON extraction |
|---|---|---|---|---|---|---|---|---|---|---|
| google/gemini-3.1-flash-lite | 92.5 | 96.7 | 93.3 | 100.0 | 73.3 | 100.0 | 100.0 | 100.0 | 60.0 | 94.1 |
| google/gemini-3.5-flash-lite | 85.0 | 90.0 | 96.7 | 93.3 | 80.0 | 100.0 | 100.0 | 100.0 | 80.0 | 92.0 |
| qwen/qwen3.8-flash | 95.0 | 93.3 | 90.0 | 80.0 | 73.3 | 100.0 | 100.0 | 100.0 | 60.0 | 92.0 |
| inclusionai/ling-3.0-flash-vl | 92.5 | 93.3 | 86.7 | 100.0 | 86.7 | 100.0 | 100.0 | 100.0 | 80.0 | 89.0 |
| z-ai/glm-5.3-flash | 87.5 | 93.3 | 90.0 | 100.0 | 73.3 | 100.0 | 100.0 | 80.0 | 60.0 | 91.9 |
| moonshotai/kimi-k2.5 | 90.0 | 90.0 | 96.7 | 73.3 | 40.0 | 80.0 | 80.0 | 80.0 | 80.0 | 92.3 |
| qwen/qwen3.6-35b-a3b | 92.5 | 100.0 | 86.7 | 100.0 | 66.7 | 100.0 | 100.0 | 100.0 | 60.0 | 82.6 |
| qwen/qwen3.5-9b | 92.5 | 93.3 | 86.7 | 93.3 | 80.0 | 100.0 | 100.0 | 100.0 | 40.0 | 81.7 |
| xiaomi/mimo-v2.6-flash | 95.0 | 83.3 | 80.0 | 73.3 | 33.3 | 100.0 | 80.0 | 80.0 | 60.0 | 88.7 |
| deepseek/deepseek-v4.1-flash | 87.5 | 93.3 | 83.3 | 86.7 | 33.3 | 80.0 | 80.0 | 80.0 | 40.0 | 86.8 |
| openai/gpt-6-luna | 85.0 | 80.0 | 80.0 | 46.7 | 6.7 | 60.0 | 40.0 | 60.0 | 20.0 | 92.3 |
| nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free | 95.0 | 96.7 | 86.7 | 80.0 | 40.0 | 100.0 | 100.0 | 100.0 | 40.0 | 67.4 |
| mistralai/mistral-small-3.2-24b-instruct | 87.5 | 86.7 | 76.7 | 33.3 | 13.3 | 80.0 | 20.0 | 60.0 | 20.0 | 81.5 |
| openai/gpt-5-nano | 90.0 | 83.3 | 80.0 | 6.7 | 6.7 | 60.0 | 40.0 | 60.0 | 40.0 | 42.6 |
