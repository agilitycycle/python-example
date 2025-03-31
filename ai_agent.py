import os
from dotenv import load_dotenv, find_dotenv
import uuid
from typing import List, Dict, Optional, Any
from openai import OpenAI
import json
from dataclasses import dataclass

# Load the .env file
load_dotenv(find_dotenv())
# Access the OpenAI API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")

# First, we define how the LLM should understand our tools
tools = [
  {
    "type": "function",
    "function": {
      "name": "query_chat",
      "description": """Query chat and return the results.""",
      "parameters": {
        "type": "object",
        "properties": {
            "query": {
              "type": "string",
              "description": """
                Must return the users original input.
              """
            }
        },
        "required": ["query"],
        "additionalProperties": False
      },
      "strict": True
    }
  }
]

def query_chat(query: str) -> str:
  # Initialize OpenAI
  client = OpenAI(api_key=api_key)
  messages = []

  messages.append({
    "role": "user",
    "content": query
  })

  messages.append({
    "role": "system",
    "content": """
      You are a helpful AI assistant with access to Open AI.
      Objective:
      1. You will be given a piece of literature in which to collaborate on.
      You must supply the next paragraph for it.

      Follow these rules:
      1. You can be creative
      2. You can be thoughtful
      3. You need to consider the central theme
      4. Who is the main character, are there any?
      5. What are they doing, what will they do next?
      6. If the response returns an error, explain the error to the user clearly
    """
  })

  completion = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools, # Global tools list
    tool_choice="auto" # Let the model decide when to use tools
  )

  response_message = completion.choices[0].message
  print(response_message)

# Memory Config
@dataclass
class MemoryConfig:
  """Configuration for memory management"""
  max_messages: int = 20 # When to summarize
  summary_length: int = 2000 # Max summary length in words
  db_connection: str = "dbname=your_db user=your_user password=your_pass"

class AgentMemory:
  def __init__(self, config: Optional[MemoryConfig] = None):
    self.config = config or MemoryConfig()
    self.session_id = uuid.uuid4()
    self.setup_database = self.setup_database()
    
  def setup_database(self):
    """Create necessary database tables if they don't exist"""

# Agent
class Agent:
  def __init__(self, system_prompt: Optional[str] = None): # init once the object is formed
    """"""

  def execute_tool(self, tool_call: Any) -> str:
    try:
      function_name = tool_call.function.name
      function_args = json.loads(tool_call.function.arguments)

      # Execute the appropriate tool. Add more here as needed.
      if function_name == "query_chat":
        result = query_chat(function_args["query"])
      else:
        result = json.dumps({
          "error": f"Unknown tool: {function_name}"
        })

      return result

    except json.JSONDecodeError:
      return json.dumps({
        "error": "Failed to parse tool arguments"
      })
    except Exception as e:
      return json.dumps({
        "error": f"Tool execution failed: {str(e)}"
      })

  def process_query(self, user_input: Any) -> str:
    self.messages.append({
      "role": "user",
      "content": user_input
    })

    try:
      max_iterations = 1 # 5
      current_iteration = 0

      while current_iteration < max_iterations:  # Limit to 5 iterations
        current_iteration += 1
        completion = self.client.chat.completions.create(
          model="gpt-4o",
          messages=self.messages,
          tools=tools, # Global tools list
          tool_choice="auto" # Let the model decide when to use tools
        )

      response_message = completion.choices[0].message
      print(response_message)

      # If no tool calls, we're done
      if not response_message.tool_calls:
        self.messages.append(response_message)
        return response_message.content

      # Add the model's thinking to conversation history
      self.messages.append(response_message)

      # Process all tool calls
      for tool_call in response_message.tool_calls:
        try:
          print("Tool call:", tool_call)
          result = self.execute_tool(tool_call)
          print("Tool executed......")
        except Exception as e:
          print("Execution failed......")
          result = json.dumps({
            "error": f"Tool execution failed: {str(e)}"
          })

          print(f"Tool result custom: {result}")

          self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(result)
          })
          print("Messages:", self.messages)

          # If we've reached max iterations, return a message indicating this
          max_iterations_message = {
            "role": "assistant",
            "content": "I've reached the maximum number of tool calls (5) without finding a complete answer. Here's what I know so far: " + response_message.content
          }
          self.messages.append(max_iterations_message)
          return max_iterations_message["content"]

    except Exception as e:
      error_message = f"Error processing query: {str(e)}"
      print(error_message)
      self.messages.append({
          "role": "assistant",
          "content": error_message
      })
      return error_message

  def get_conversation_history(self) -> List[Dict[str, str]]:
    print("Get conversation history")

# Update Agent Class to use memory.
class AgentWithMemory(Agent):
  def __init__(self, memory_config: Optional[MemoryConfig] = None): # give agent memory
    # Initialize OpenAI
    self.client = OpenAI(api_key=api_key)
    self.memory = AgentMemory(memory_config)
    self.messages = []

    default_prompt = """
      You are a helpful AI assistant with access to OpenAI. Follow these rules:
        1. When given a story you will query chat
        4. Always mention your source of information
        5. If a tool returns an error, explain the error to the user clearly
      """

    self.messages.append({
      "role": "system",
      "content": default_prompt
    })
    
  def process_query(self, user_input: str) -> str:
    super().process_query(user_input)

  def execute_tool(self, tool_call: Any) -> str:
    super().execute_tool(tool_call)