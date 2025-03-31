from ai_agent import AgentWithMemory, MemoryConfig

# Create an agent
agent = AgentWithMemory(
  memory_config=MemoryConfig(
    max_messages=10, # summarize after 10 messages
    db_connection="postgresql://user:pass@localhost/your_db"
  )
)

# Simple interaction
def chat_with_agent(user_input: str):
  print(f"\nUser: {user_input}")
  print(f"Assistant: {agent.process_query(user_input)}")

if __name__ == "__main__":
  chat_with_agent("ONCE UPON A TIME, a Princess named Snow White lived in a castle with her father the King and her Stepmother the Queen.")
  # chat_with_agent("The perfect sermon is not about perfection in one's sermon but about one's walk in Christ.")