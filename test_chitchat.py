import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import agent

conversation_sequence = [
    "hi",
    "how are you",
    "can you help me with something",
    "I want to check on our deals",
    "okay show me the top ones"
]

history = []

for idx, user_msg in enumerate(conversation_sequence, 1):
    print(f"==================================================")
    print(f"TURN {idx}: USER -> '{user_msg}'")
    print(f"==================================================")
    response = agent.run_agent(user_msg, history)
    print(f"ASSISTANT:\n{response}\n")
    history.append({"role": "user", "content": user_msg})
    history.append({"role": "assistant", "content": response})
