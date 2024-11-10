from langchain.agents import initialize_agent
from langchain.agents.agent_toolkits import ZapierToolkit
from langchain.utilities.zapier import ZapierNLAWrapper
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI

from langchain.chains import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from utils import extract_information
from templates import template_1

system_message_prompt = SystemMessagePromptTemplate.from_template(template_1)
human_template="{query}"
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt,human_message_prompt])

# Assigning model and tools
chat = ChatOpenAI(model="gpt-4o",temperature=0.6)
memory = ConversationBufferMemory(memory_key="chat_history")

#zapier wrapper agent
zapier = ZapierNLAWrapper()
toolkit = ZapierToolkit.from_zapier_nla_wrapper(zapier)
tools = toolkit.get_tools() 

def bot_response(query):
    """
    Function to handle the conversation flow with the chatbot.
    
    Args:
    - query (str): The user input/query
    
    Returns:
    - response (str): The bot response
    """
    conversation = []
    conversation.append('User: ' + query)

    output = gpt_response(query)
    conversation.append('Bot: ' + output)

    print(conversation)

    # Extract information
    pattern_name = r'\bFull Name:\s*(.*)'
    pattern_service = r'\bService Type:\s*(.*)'
    pattern_location = r'\bLocation:\s*(.*)'
    pattern_time = r'\bdatetime:\s*(.*)'
    pattern_email = r'\bEmail Address:\s*(.*)'

    name = extract_information(conversation, pattern_name)
    service = extract_information(conversation, pattern_service)
    location = extract_information(conversation, pattern_location)
    datetime = extract_information(conversation, pattern_time)
    email = extract_information(conversation, pattern_email)

    # Check if all information is collected
    if name and service and location and datetime and email:
        # Perform actions
        conversation.append("""
            Make use of this {tools} to schedule a meeting on a google meets and add it to the google calander based on collected information
            Also, Use {tools} for sending an email to the user provided email address in the below format:
            
            ####
            
            Dear [Full Name],
            
            I hope this email finds you well. We are writing to confirm the details of scheduled quick call with me.
            Please review the information below:
            
            Service Type: [Service Type]
            Location: [Location]
            datetime: [datetime]
            Link: [Google Meet Link]

            If you have any questions or need to make any changes, please don't hesitate to reach out to me. You can reply to this email or contact us directly at (000)-000 0000.

            I look forward to meeting with you on [datetime]. Thank you for choosing my service, and I am excited to assist you.

            Best regards,
            Sanchuka Nirupama.
            
            ####
            .
        """)

        # Run agent chain
        scheduler = agent_chain.run(conversation)
        print(scheduler)
        return scheduler

    return output


#Chat Cain
def gpt_response(query):
    
    chain = LLMChain(llm = chat, prompt = chat_prompt, memory = memory)
    response = chain.run(query)
    
    return response        

#Agent Chain
agent_chain = initialize_agent(tools, llm = chat, agent = "zero-shot-react-description", verbose = True)
