import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import Tool
from langchain.utilities import DuckDuckGoSearchAPIWrapper
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END, MessagesState
import json
import sys
from pathlib import Path

# Add src to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from soil_fertility_detection_v3 import SoilFertilityClassifier
from knowledge_base_query import query_knowledge_base
import season_crop_predictor as scp

# Set environment variable for the API key (replace with your actual key)
os.environ["GOOGLE_API_KEY"] = 'AIzaSyBsDwt27kOVM1CrRyTLmHZPCEjswt-6qUM'

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)

# DuckDuckGo search wrapper
ddg_search = DuckDuckGoSearchAPIWrapper()

# Initialize soil classifier
classifier = SoilFertilityClassifier()

# Search tool function
def web_search(query: str) -> str:
    """Searches the web for the provided query."""
    return ddg_search.run(query)

# Soil analysis tool
def soil_analysis(query: str) -> str:
    """Analyzes soil fertility based on provided parameters."""
    try:
        # Parse parameters from query (expecting JSON-like format)
        # Example: "nitrogen: 50, phosphorus: 20, potassium: 150, ph: 6.5, ec: 0.8, oc: 0.5"
        params = {}
        for part in query.split(','):
            if ':' in part:
                key, value = part.split(':', 1)
                key = key.strip().lower()
                value = float(value.strip())
                if key in ['nitrogen', 'phosphorus', 'potassium', 'ph', 'ec', 'oc', 'sulfur', 'zinc', 'iron', 'boron']:
                    params[key] = value

        if len(params) < 6:
            return "Please provide at least nitrogen, phosphorus, potassium, pH, EC, and OC values."

        # Run analysis
        result = classifier.apply_liebig_law(
            params.get('nitrogen', 0),
            params.get('phosphorus', 0),
            params.get('potassium', 0),
            params.get('ph', 0),
            params.get('ec', 0),
            params.get('oc', 0)
        )

        response = f"Soil Analysis Result:\n"
        response += f"Classification: {result.get('classification', 'MODERATE')}\n"
        response += f"Fertility Score: {result.get('fertility_score', 150)}\n"
        response += f"Limiting Factor: {result.get('limiting_factor', 'None')}\n"
        if result.get('limiting_factor'):
            response += f"Recommendation: Address {result.get('limiting_factor')} deficiency to improve fertility."

        return response
    except Exception as e:
        return f"Error in soil analysis: {str(e)}"

# Crop recommendation tool
def crop_recommendation(query: str) -> str:
    """Provides crop recommendations based on season and region."""
    try:
        # Parse season and region from query
        season = "Kharif"  # default
        region = "Punjab"  # default

        if "kharif" in query.lower():
            season = "Kharif"
        elif "rabi" in query.lower():
            season = "Rabi"
        elif "zaid" in query.lower():
            season = "Zaid"

        # Extract region if mentioned
        regions = ["Punjab", "Haryana", "UP", "Bihar", "Rajasthan", "MP", "Gujarat", "Maharashtra", "Karnataka", "Tamil Nadu", "AP", "Telangana"]
        for reg in regions:
            if reg.lower() in query.lower():
                region = reg
                break

        # Get crops for the season
        recommendations = scp.crops_for_season(season)

        response = f"Crop Recommendations for {season} season in {region}:\n"
        if recommendations:
            response += "\n".join(f"- {crop}" for crop in recommendations)
        else:
            response += "Rice, Wheat, Maize (default recommendations)"

        return response
    except Exception as e:
        return f"Error in crop recommendation: {str(e)}"

# Knowledge base query tool
def knowledge_query(query: str) -> str:
    """Queries the soil knowledge base for information."""
    try:
        result = query_knowledge_base(query, top_k=3, use_llm=True)

        if isinstance(result, dict):
            response = f"Knowledge Base Answer:\n{result.get('answer', 'No answer found')}\n"
            response += f"Confidence: {result.get('confidence', 0)}\n"
            response += f"Sources: {result.get('source_count', 0)}"
            return response
        else:
            return "Unable to retrieve information from knowledge base."
    except Exception as e:
        return f"Error in knowledge query: {str(e)}"

# Create tools
search_tool = Tool.from_function(
    name="web_search",
    func=web_search,
    description="Searches the web to get general information about agriculture, soil science, and farming practices."
)

soil_tool = Tool.from_function(
    name="soil_analysis",
    func=soil_analysis,
    description="Analyzes soil fertility based on provided nutrient parameters (nitrogen, phosphorus, potassium, pH, EC, OC)."
)

crop_tool = Tool.from_function(
    name="crop_recommendation",
    func=crop_recommendation,
    description="Provides crop recommendations based on season (Kharif/Rabi/Zaid) and region in India."
)

knowledge_tool = Tool.from_function(
    name="knowledge_query",
    func=knowledge_query,
    description="Queries the specialized soil science knowledge base for detailed information on soil management, fertilizers, and agricultural practices."
)

class SoilConsultancyBot:
    """AI-powered Soil Consultancy Bot using LangGraph agent."""

    def __init__(self):
        # Create memory store
        self.memory = MemorySaver()

        # Create the agent with soil-related tools
        tools = [search_tool, soil_tool, crop_tool, knowledge_tool]
        self.agent = create_react_agent(llm, tools, checkpointer=self.memory)

        # Create workflow graph
        self.workflow = StateGraph(MessagesState)

        # Define the agent call function
        def call_model(state: MessagesState):
            messages = state['messages']
            response = self.agent.invoke({"messages": messages})
            return {"messages": [response["messages"][-1]]}

        # Add edges to workflow graph
        self.workflow.add_node("agent", call_model)
        self.workflow.add_edge(START, "agent")
        self.workflow.add_edge("agent", END)

        # Compile the workflow
        self.app = self.workflow.compile()

        # Counselor prompt for soil consultancy
        self.counselor_prompt = '''
        You are a friendly and knowledgeable Soil Science Consultant chatbot named "SoilPro Advisor!" specializing in helping farmers and agricultural professionals with soil fertility analysis, crop recommendations, and farming advice. Think of yourself as a personalized, expert soil consultant!

        Introduction: Start by introducing yourself warmly and asking for the user's name or their farming context.

        Understanding the User:
            Ask about their location/region in India.
            Inquire about their farming experience and current crops.
            Request information about their soil testing results or parameters they have.

        Soil Analysis:
            Guide users on what soil parameters to test (N, P, K, pH, EC, OC, etc.).
            Use the soil_analysis tool when users provide parameter values.
            Explain fertility classifications and limiting factors clearly.

        Crop Recommendations:
            Ask about the season (Kharif, Rabi, Zaid) and region.
            Use the crop_recommendation tool to provide suitable crops.
            Consider local climate and soil conditions.

        Knowledge Base Queries:
            Use the knowledge_query tool for detailed information on soil management, fertilizers, pest control, etc.
            Provide practical, actionable advice based on agricultural research.

        General Advice:
            Offer guidance on sustainable farming practices.
            Suggest when to consult local agricultural experts.
            Provide information on government schemes and subsidies.

        Conversational Tone: Maintain an encouraging and supportive tone throughout the interaction, ensuring advice feels personal and practical.
        '''

    def get_response(self, user_input: str, session_id: str = "soil_session") -> str:
        """Get a response from the soil consultancy bot for the given user input."""
        try:
            # Configure the agent thread
            config = {"configurable": {"thread_id": session_id}}

            # Create messages with counselor prompt and user input
            messages = [
                HumanMessage(content=self.counselor_prompt),
                HumanMessage(content=user_input)
            ]

            # Call the agent
            response = self.app.invoke({"messages": messages}, config)

            # Return the last message content
            return response["messages"][-1].content

        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question."

# Example usage (can be removed in production)
if __name__ == "__main__":
    bot = SoilConsultancyBot()
    print("SoilPro Advisor initialized. Ready for queries!")

    # Test the bot
    test_query = "What crops should I grow in Punjab during Kharif season?"
    response = bot.get_response(test_query)
    print(f"Query: {test_query}")
    print(f"Response: {response}")
