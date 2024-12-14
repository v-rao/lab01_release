from typing import Dict, List
from autogen import ConversableAgent
import sys
import os

def fetch_restaurant_data(restaurant_name: str) -> Dict[str, List[str]]:
    reviews = []
    with open("restaurant-data.txt", "r") as file:
        for line in file:
            if line.lower().startswith(restaurant_name.lower()):
                reviews.append(line.strip())
    return reviews


def calculate_overall_score(restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]) -> Dict[str, float]:
    # Validate inputs
    assert len(food_scores) == len(customer_service_scores), "Scores lists must be of equal length."
    
    N = len(food_scores)
    total_score = 0
    for food_score, service_score in zip(food_scores, customer_service_scores):
        total_score += math.sqrt(food_score**2 * service_score)
    
    overall_score = total_score * (1 / (N * math.sqrt(125))) * 10
    return {restaurant_name: round(overall_score, 3)}

def get_data_fetch_agent_prompt(restaurant_query: str) -> str:
    return f"Fetch reviews for the restaurant '{restaurant_query}'. Ensure to retrieve accurate and relevant reviews."

# TODO: feel free to write as many additional functions as you'd like.

# Do not modify the signature of the "main" function.
def main(user_query: str):
    entrypoint_agent_system_message = (
        "You are a helpful assistant capable of coordinating with other agents to provide restaurant data and insights."
        "Your goal is to answer the user's query by fetching reviews and calculating scores based on provided metrics."
    )
    # example LLM config for the entrypoint agent
    llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": os.environ.get("OPENAI_API_KEY")}]}
    # the main entrypoint/supervisor agent
    entrypoint_agent = ConversableAgent("entrypoint_agent", 
                                        system_message=entrypoint_agent_system_message, 
                                        llm_config=llm_config)
    # entrypoint_agent.register_for_llm(name="fetch_restaurant_data", description="Fetches the reviews for a specific restaurant.")(fetch_restaurant_data)
    # entrypoint_agent.register_for_execution(name="fetch_restaurant_data")(fetch_restaurant_data)

    # other agents
    data_fetch_agent = ConversableAgent("data_fetch_agent", 
                                      system_message=entrypoint_agent_system_message, 
                                        llm_config=llm_config)
    review_analysis_agent = ConversableAgent("review_analysis_agent", 
                                        system_message=entrypoint_agent_system_message, 
                                        llm_config=llm_config)
    scoring_agent = ConversableAgent("scoring_agent", 
                                        system_message=entrypoint_agent_system_message, 
                                        llm_config=llm_config) 
    
    # # Example usage of agents in a conversation
    # # This setup simulates a chat interaction where data is fetched and then scored.
    # restaurant_name = user_query
    # reviews_result = fetch_restaurant_data(restaurant_name)
    # if restaurant_name in reviews_result:
    #     reviews = reviews_result[restaurant_name]
    #     print(f"Reviews for {restaurant_name}:")
    #     for review in reviews:
    #         print(f"- {review}")
        
    #     # Example scores for demonstration
    #     food_scores = [4, 3, 5]
    #     customer_service_scores = [5, 4, 3]
    #     score_result = calculate_overall_score(restaurant_name, food_scores, customer_service_scores)
    #     print(f"Overall Score for {restaurant_name}: {score_result[restaurant_name]}")
    # else:
    #     print(f"No data available for the restaurant '{restaurant_name}'.")

    result = entrypoint_agent.initiate_chats(
        [
            {
                "recipient": data_fetch_agent,
                "message": f"The question is: {user_query}",
                "max_turns": 2,
                "summary_method": "last_msg",
            },
            {
                "recipient": review_analysis_agent,
                "message": "These are the reviews",
                "max_turns": 1,
                "summary_method": "reflection_with_llm",
                "summary_args": {"summary_prompt":"some prompt"},
            },
            {
                "recipient": scoring_agent,
                "message": "These are raw scores",
                "max_turns": 2,
                "summary_method": "last_msg",
            },
        ]
    )
    
    # TODO
    # Fill in the argument to `initiate_chats` below, calling the correct agents sequentially.
    # If you decide to use another conversation pattern, feel free to disregard this code.
    
    # Uncomment once you initiate the chat with at least one agent.
    # result = entrypoint_agent.initiate_chats([{}])
    
# DO NOT modify this code below.
# if __name__ == "__main__":
#     assert len(sys.argv) > 1, "Please ensure you include a query for some restaurant when executing main."
#     main(sys.argv[1])