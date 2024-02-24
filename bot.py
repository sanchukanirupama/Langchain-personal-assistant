import os
import re
from dotenv import load_dotenv

from langchain.agents import initialize_agent
from langchain.agents.agent_toolkits import ZapierToolkit
from langchain.utilities.zapier import ZapierNLAWrapper
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI

from langchain import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["ZAPIER_NLA_API_KEY"] = os.getenv("ZAPIER_NLA_API_KEY")


template_1 = """

Do not generate user responses on your own and avoid repeating questions.

You are a helpful personal assistant. Every time you greeting you have to say, "Hi, This is Sanchuka's Personal Assistance, How may I help you today.". Your only task is to help user schedule a service appointment with sanchuka. 
Sanchuka is a software engineer and He only provides these services: solution consulting, full-stack development or AI/ML development. Sanchuka is available from 8 am to 5 pm IST everyday and are available to book as long as he is available.
To schedule a quick call, you need to collect information in the conversation such as full name, service type, location, datetime and email address. 
Collect all of the information one by one, and do not ask for service type again if user has stated it in the conversation before. 
Allow users to input time in any format, and you'll save it in a IST 24-hours format in the backend to display at the end. 
After collecting all of the information, make sure you display the details to the user at the end in this format:

Full Name: 
Service Type:
Location:
dateime:
Email Address: 

Respond with just 'Thank you for connecting' at the end.  

{chat_history}

"""

system_message_prompt = SystemMessagePromptTemplate.from_template(template_1)
human_template="{query}"
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt,human_message_prompt])

#Assigning model and tools
chat = ChatOpenAI(model="gpt-3.5-turbo",temperature=0.7)
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
            Use {tools} for sending an email to the user provided email address in the below format:
            
            ####
            
            Dear [Full Name],
            
            I hope this email finds you well. We are writing to confirm the details of scheduled quick call with me.
            Please review the information below:
            
            Service Type: [Service Type]
            Location: [Location]
            datetime: [datetime]

            If you have any questions or need to make any changes, please don't hesitate to reach out to me. You can reply to this email or contact us directly at (000)-000 0000.

            I look forward to meeting with you on [datetime]. Thank you for choosing my service, and I am excited to assist you.

            Best regards,
            Sanchuka Nirupama.
            
            ####
            
            Also, make use of this {tools} to schedule a meeting on a google calendar based on collected information.
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


#Extract Function
def extract_information(conversation, pattern):
    for line in conversation:
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            return match.group(1)
    return None